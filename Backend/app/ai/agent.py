import google.generativeai as genai
from google.generativeai.types import content_types
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any, Optional
import json
import re
from app.core.config import settings
from app.models.models import Variant, Product, Job, Customer, Alert, JobMaterial, Category, Subcategory

class HardwareTools:
    """
    Exposes clean python backend services as structured tools for Gemini.
    These methods interact only with SQLAlchemy session and return basic serializable structures.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_low_stock_items(self) -> Dict[str, Any]:
        """
        Retrieves all inventory items that are currently running below their defined reorder threshold.
        
        Returns:
            A dictionary containing a list of low stock variants, their current quantity, and units.
        """
        variants = self.db.query(Variant).join(Product).filter(
            Variant.quantity <= Variant.reorder_threshold
        ).all()
        
        items = []
        for v in variants:
            items.append({
                "SKU": v.SKU,
                "product_name": v.product.name,
                "dimensions": v.dimensions,
                "color": v.color,
                "finish": v.finish,
                "quantity_left": v.quantity,
                "reorder_threshold": v.reorder_threshold,
                "unit": v.unit,
                "price": v.price
            })
        return {"low_stock_items": items, "count": len(items)}

    def get_variant_stock(self, sku: str) -> Dict[str, Any]:
        """
        Retrieves the exact available stock level and details for a given unique SKU code.
        
        Args:
            sku: The unique SKU code of the product (e.g. 'TI-WM-KM-2X2').
        """
        variant = self.db.query(Variant).join(Product).filter(
            Variant.SKU.ilike(sku.strip())
        ).first()
        
        if not variant:
            return {"error": f"Product with SKU '{sku}' not found."}
            
        return {
            "SKU": variant.SKU,
            "product_name": variant.product.name,
            "quantity_available": variant.quantity,
            "unit": variant.unit,
            "price": variant.price,
            "dimensions": variant.dimensions,
            "color": variant.color,
            "finish": variant.finish,
            "reorder_threshold": variant.reorder_threshold
        }

    def get_job_status(self, job_name: str) -> Dict[str, Any]:
        """
        Retrieves detailed execution status, timeline, customer information, and assigned/consumed
        materials for a specific store renovation or building project.
        
        Args:
            job_name: The name or partial name of the job (e.g. 'Bathroom Renovation').
        """
        job = self.db.query(Job).join(Customer).filter(
            Job.name.ilike(f"%{job_name.strip()}%")
        ).first()
        
        if not job:
            return {"error": f"Job named '{job_name}' not found."}
            
        materials = []
        for m in job.materials:
            materials.append({
                "SKU": m.variant.SKU,
                "product_name": m.variant.product.name,
                "quantity_assigned": m.quantity_assigned,
                "quantity_consumed": m.quantity_consumed,
                "unit": m.variant.unit,
                "status": m.status
            })
            
        return {
            "id": str(job.id),
            "job_name": job.name,
            "customer_name": job.customer.name,
            "status": job.status,
            "start_date": job.start_date.isoformat() if job.start_date else None,
            "deadline": job.deadline.isoformat() if job.deadline else None,
            "assigned_materials": materials,
            "notes": job.notes
        }

    def get_customer_jobs(self, customer_name: str) -> Dict[str, Any]:
        """
        Retrieves all construction projects or jobs associated with a specific customer family or account.
        
        Args:
            customer_name: The name of the customer (e.g. 'Sharma Family' or 'Sharma').
        """
        customer = self.db.query(Customer).filter(
            Customer.name.ilike(f"%{customer_name.strip()}%")
        ).first()
        
        if not customer:
            return {"error": f"Customer '{customer_name}' not found."}
            
        jobs = []
        for j in customer.jobs:
            jobs.append({
                "id": str(j.id),
                "job_name": j.name,
                "status": j.status,
                "deadline": j.deadline.isoformat() if j.deadline else None
            })
            
        return {
            "customer_name": customer.name,
            "phone": customer.phone,
            "email": customer.email,
            "jobs": jobs
        }

    def get_inventory_summary(self) -> Dict[str, Any]:
        """
        Retrieves aggregated telemetry on the inventory including total unique categories, unique SKUs,
        total calculated store stock valuation, and active alerts.
        """
        categories_count = self.db.query(Category).count()
        products_count = self.db.query(Product).count()
        variants = self.db.query(Variant).all()
        
        total_valuation = 0.0
        total_items = 0.0
        for v in variants:
            total_items += v.quantity
            total_valuation += (v.quantity * v.price)
            
        unresolved_alerts = self.db.query(Alert).filter(Alert.is_resolved == False).count()
        pending_jobs = self.db.query(Job).filter(Job.status == "Pending").count()
        active_jobs = self.db.query(Job).filter(Job.status == "In_Progress").count()
        
        return {
            "total_categories": categories_count,
            "total_unique_products": products_count,
            "total_skus": len(variants),
            "total_physical_quantity": total_items,
            "total_stock_value_rupees": round(total_valuation, 2),
            "active_low_stock_alerts": unresolved_alerts,
            "jobs_summary": {
                "pending": pending_jobs,
                "in_progress": active_jobs
            }
        }


def run_chat_query(db: Session, message: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Executes chatbot query. First tries Gemini with instance-bound python tools.
    If the API key is not configured, automatically invokes the deterministic regex parser fallback.
    """
    tools_provider = HardwareTools(db)
    
    # Graceful fallback: If Gemini key is missing or dummy
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY in ["your_key_here", ""]:
        return run_deterministic_fallback(tools_provider, message)
        
    try:
        # Initialize Google GenAI
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Expose the tool methods as function definitions
        # To bypass self issues, we wrap them in lambda/plain functions or pass bounded methods
        tools_list = [
            tools_provider.get_low_stock_items,
            tools_provider.get_variant_stock,
            tools_provider.get_job_status,
            tools_provider.get_customer_jobs,
            tools_provider.get_inventory_summary
        ]
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=tools_list,
            system_instruction=(
                "You are an intelligent, operational chatbot for a hardware store dashboard. "
                "You help employees and admins query inventory stock, low items, customer jobs, and system summaries. "
                "Always use the provided functions/tools to fetch real data before answering. "
                "Do NOT make up values or mock details. "
                "Keep responses concise, factual, professional, and formatted in clean markdown. "
                "If a product is low in stock or a job deadline is near, highlight it politely."
            )
        )
        
        # Build conversational history
        contents = []
        if chat_history:
            for turn in chat_history:
                role = "user" if turn.get("role") == "user" else "model"
                contents.append(content_types.to_content({"role": role, "parts": [turn.get("content")]}))
        
        # Append current user prompt
        contents.append(content_types.to_content({"role": "user", "parts": [message]}))
        
        # Make request to Gemini
        response = model.generate_content(contents)
        
        # Process potential function calls in loop (up to 3 iterations for multi-step)
        for _ in range(3):
            # If no function calls are returned, exit loop
            if not response.candidates or not response.candidates[0].content.parts:
                break
                
            function_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
            if not function_calls:
                break
                
            # Execute all function calls
            tool_responses = []
            for call in function_calls:
                func_name = call.name
                args = dict(call.args)
                
                # Retrieve matching tool method
                tool_method = getattr(tools_provider, func_name, None)
                if tool_method:
                    try:
                        result = tool_method(**args)
                    except Exception as e:
                        result = {"error": str(e)}
                else:
                    result = {"error": f"Tool '{func_name}' not implemented"}
                    
                tool_responses.append({
                    "function_response": {
                        "name": func_name,
                        "response": result
                    }
                })
            
            # Feed back responses to Gemini to compile natural text
            contents.append(response.candidates[0].content)
            contents.append(content_types.to_content({"role": "model", "parts": tool_responses}))
            
            # Request next generation
            response = model.generate_content(contents)
            
        return response.text if response.text else "I resolved your request, but could not compile a textual summary."
        
    except Exception as e:
        # Fall back to deterministic parsing if any error occurs
        return f"*(Running in deterministic offline mode due to: {str(e)})*\n\n" + run_deterministic_fallback(tools_provider, message)


def run_deterministic_fallback(tools: HardwareTools, message: str) -> str:
    """
    A robust regex-based keyword parser that mimics Gemini by matching key intents
    and invoking the exact same backend-bound tool parameters.
    """
    msg = message.lower()
    
    # 1. Summary Queries
    if any(k in msg for k in ["summary", "overview", "telemetry", "valuation", "total categories", "how many categories"]):
        res = tools.get_inventory_summary()
        return (
            f"### Store Telemetry Summary\n"
            f"* **Total Unique Categories**: {res['total_categories']}\n"
            f"* **Total Unique Products**: {res['total_unique_products']}\n"
            f"* **Total Tracked SKUs**: {res['total_skus']}\n"
            f"* **Physical Stock On Hand**: {res['total_physical_quantity']} items\n"
            f"* **Est. Stock Valuation**: ₹{res['total_stock_value_rupees']:,}\n"
            f"* **Active Low Stock Alerts**: {res['active_low_stock_alerts']}\n"
            f"* **Active Job Projects**: {res['jobs_summary']['in_progress']} active, {res['jobs_summary']['pending']} pending."
        )

    # 2. Low Stock Queries
    if any(k in msg for k in ["low stock", "running low", "what is low", "reorder"]):
        res = tools.get_low_stock_items()
        if res["count"] == 0:
            return "All products are currently well-stocked. No low-stock alerts are active."
            
        lines = [f"### Active Low Stock Alerts ({res['count']})", ""]
        lines.append("| SKU | Product | Size/Finish | Stock | Min |")
        lines.append("| --- | --- | --- | --- | --- |")
        for item in res["low_stock_items"]:
            desc = f"{item['dimensions'] or ''} {item['color'] or ''} {item['finish'] or ''}".strip()
            lines.append(f"| `{item['SKU']}` | {item['product_name']} | {desc} | **{item['quantity_left']}** {item['unit']} | {item['reorder_threshold']} |")
        return "\n".join(lines)

    # 3. Variant Specific Stock (SKU Lookup)
    sku_match = re.search(r'([a-zA-Z]{2,4}-[a-zA-Z0-9]+-[a-zA-Z0-9\-]+)', message)
    if sku_match or "sku" in msg or "variant" in msg:
        sku = sku_match.group(1) if sku_match else ""
        if not sku:
            # Fallback if no exact SKU format found, search for generic names
            for word in message.split():
                if len(word) > 4 and "-" in word:
                    sku = word
                    break
        if sku:
            res = tools.get_variant_stock(sku)
            if "error" in res:
                return f"I couldn't find a SKU matching `{sku}`. Could you please double-check the spelling?"
            desc = f"{res['dimensions'] or ''} {res['color'] or ''} {res['finish'] or ''}".strip()
            status = "⚠️ LOW STOCK" if res['quantity_available'] <= res['reorder_threshold'] else "✅ Well-stocked"
            return (
                f"### SKU Details: `{res['SKU']}`\n"
                f"* **Product**: {res['product_name']}\n"
                f"* **Specs**: {desc}\n"
                f"* **Stock Level**: **{res['quantity_available']}** {res['unit']} ({status})\n"
                f"* **Reorder Limit**: {res['reorder_threshold']} {res['unit']}\n"
                f"* **Retail Price**: ₹{res['price']:,} per {res['unit']}"
            )

    # 4. Customer Job Lookup
    customer_keywords = ["customer", "family", "project for", "jobs for", "job for"]
    if any(k in msg for k in customer_keywords) or "sharma" in msg:
        name = "Sharma"  # Default fallback seed name
        for word in message.split():
            if word.istitle() and word not in ["Customer", "Family", "Job", "Project", "I", "What", "How", "Show"]:
                name = word
                break
        res = tools.get_customer_jobs(name)
        if "error" in res:
            return f"I couldn't find a customer record matching '{name}'."
            
        lines = [f"### Active Jobs for Customer: **{res['customer_name']}**", ""]
        if not res["jobs"]:
            lines.append("No active job projects found for this customer.")
        else:
            for job in res["jobs"]:
                lines.append(f"* **{job['job_name']}** (Status: `{job['status']}`, Deadline: {job['deadline'] or 'N/A'})")
        return "\n".join(lines)

    # 5. Specific Job Material Lookup
    if any(k in msg for k in ["job", "project", "renovation", "materials in", "what was used in"]):
        job_name = "Bathroom"
        # Extract capital words representing job names
        matches = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', message)
        filtered = [m for m in matches if m not in ["I", "What", "How", "Show", "Customer", "Sharma", "Family"]]
        if filtered:
            job_name = filtered[0]
            
        res = tools.get_job_status(job_name)
        if "error" in res:
            return f"I couldn't find a job matching name '{job_name}'."
            
        lines = [
            f"### Job Status: **{res['job_name']}**",
            f"* **Customer**: {res['customer_name']}",
            f"* **Project Status**: `{res['status']}`",
            f"* **Target Deadline**: {res['deadline'][:10] if res['deadline'] else 'N/A'}",
            f"* **Notes**: {res['notes'] or ''}",
            "",
            "#### Assigned Materials Tracking:",
            "| Material SKU | Name | Assigned | Consumed | Status |",
            "| --- | --- | --- | --- | --- |"
        ]
        
        if not res["assigned_materials"]:
            lines.append("| - | No materials assigned | - | - | - |")
        else:
            for mat in res["assigned_materials"]:
                lines.append(f"| `{mat['SKU']}` | {mat['product_name']} | {mat['quantity_assigned']} {mat['unit']} | {mat['quantity_consumed']} {mat['unit']} | {mat['status']} |")
                
        return "\n".join(lines)

    # 6. Fallback General Guidelines
    return (
        "I am your store AI Assistant. I can help you inspect inventory stocks and project statuses.\n\n"
        "Here are some example questions you can ask me:\n"
        "1. *'Show a summary of inventory counts'* (Get general telemetry)\n"
        "2. *'What is low in stock?'* (Fetch active alerts)\n"
        "3. *'How many wall tiles are left?'* or *'Show variant stock for SKU TI-WM-KM-2X2'* (Get SKU stock levels)\n"
        "4. *'What jobs are registered for Sharma?'* (Retrieve customer records)\n"
        "5. *'What materials were assigned to Sharma Bathroom Renovation?'* (Retrieve specific job inventories)"
    )
