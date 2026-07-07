from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import logging
from app.db.session import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.models import (
    User, Customer, Category, Subcategory, Product, Variant,
    InventoryTransaction, Job, JobMaterial, Supplier, SupplierOrder, SupplierOrderItem, Alert, AuditLog
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_db():
    # Auto-create database if it doesn't exist on standard localhost defaults
    try:
        from sqlalchemy import create_engine, text
        temp_engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres", isolation_level="AUTOCOMMIT")
        with temp_engine.connect() as conn:
            conn.execute(text("CREATE DATABASE hardware_store_ai"))
        logger.info("Created database 'hardware_store_ai' successfully.")
    except Exception as e:
        logger.info(f"Database pre-existence check: {str(e)}")

    # Ensure tables are initialized
    logger.info("Initializing database schema tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    # Check if database is already seeded by checking default users
    admin_exists = db.query(User).filter(User.username == "admin").first()
    if admin_exists:
        logger.info("Database already seeded. Skipping seeding.")
        db.close()
        return
    
    logger.info("Starting database seeding...")
    
    try:
        # 1. Create Default Users (Admin and Employee)
        admin_user = User(
            username="admin",
            email="admin@hardwarestore.com",
            password_hash=get_password_hash("admin123"),
            role="Admin"
        )
        employee_user = User(
            username="employee",
            email="employee@hardwarestore.com",
            password_hash=get_password_hash("employee123"),
            role="Employee"
        )
        db.add_all([admin_user, employee_user])
        db.flush()
        logger.info("Created system accounts 'admin' and 'employee'.")

        # 2. Create Categories & Subcategories & Products & Variants
        # Category A: Tiles
        cat_tiles = Category(name="Tiles", description="Ceramic, porcelain, vitrified, and marble series floor and wall coverings.")
        db.add(cat_tiles)
        db.flush()

        sub_wall_tiles = Subcategory(category_id=cat_tiles.id, name="Wall Tiles", description="Designer high-gloss and matte wall tiles.")
        sub_floor_tiles = Subcategory(category_id=cat_tiles.id, name="Floor Tiles", description="Anti-skid and heavy vitrified floor tiles.")
        db.add_all([sub_wall_tiles, sub_floor_tiles])
        db.flush()

        prod_kajaria_marble = Product(subcategory_id=sub_wall_tiles.id, name="Kajaria Marble Series", description="High-definition glazed vitrified marble replication.")
        prod_somany_plank = Product(subcategory_id=sub_floor_tiles.id, name="Somany Wood Plank", description="Textured wood finishing anti-skid porcelain planks.")
        db.add_all([prod_kajaria_marble, prod_somany_plank])
        db.flush()

        var_white_matte = Variant(
            product_id=prod_kajaria_marble.id,
            SKU="TI-WM-KM-2X2",
            price=120.0,
            dimensions="2x2 ft",
            color="White",
            finish="Matte",
            quantity=0.0, # Will be set via transactions
            reorder_threshold=100.0,
            unit="sq ft",
            attributes={"finish": "matte", "resistance_class": "PEI 3", "box_coverage_sqft": 16.0}
        )
        var_oak_brown = Variant(
            product_id=prod_somany_plank.id,
            SKU="TI-FP-SW-840",
            price=180.0,
            dimensions="8x40 inch",
            color="Oak Brown",
            finish="Wood Grain Textured",
            quantity=0.0,
            reorder_threshold=50.0,
            unit="sq ft",
            attributes={"wood_type": "oak", "anti_skid": True, "box_coverage_sqft": 10.0}
        )
        db.add_all([var_white_matte, var_oak_brown])
        db.flush()

        # Category B: Bathroom Fittings
        cat_fittings = Category(name="Bathroom Fittings", description="Premium taps, wall mixers, showers, and accessories.")
        db.add(cat_fittings)
        db.flush()

        sub_taps = Subcategory(category_id=cat_fittings.id, name="Taps & Faucets", description="Single lever mixers and premium taps.")
        sub_showers = Subcategory(category_id=cat_fittings.id, name="Showers", description="Overhead rain showers and hand showers.")
        db.add_all([sub_taps, sub_showers])
        db.flush()

        prod_jaquar_mixer = Product(subcategory_id=sub_taps.id, name="Jaquar Alive Basin Mixer", description="Alive series single lever basin mixer chrome body.")
        db.add(prod_jaquar_mixer)
        db.flush()

        var_jaquar_tap = Variant(
            product_id=prod_jaquar_mixer.id,
            SKU="BF-ABM-JQ-01",
            price=4200.0,
            dimensions="Standard",
            color="Chrome Silver",
            finish="Polished Chrome",
            quantity=0.0,
            reorder_threshold=3.0,
            unit="pieces",
            attributes={"material": "brass", "warranty_years": 10}
        )
        db.add(var_jaquar_tap)
        db.flush()

        # Category C: Toilet Seats
        cat_toilets = Category(name="Toilet Seats & Sanitaryware", description="Commodes, flush valves, and seat covers.")
        db.add(cat_toilets)
        db.flush()

        sub_commodes = Subcategory(category_id=cat_toilets.id, name="Commodes", description="Wall-hung and floor-mounted European water closets.")
        db.add_all([sub_commodes])
        db.flush()

        prod_hindware_seat = Product(subcategory_id=sub_commodes.id, name="Hindware Italian WC", description="Hindware Italian Collection Wall Hung Closet.")
        db.add(prod_hindware_seat)
        db.flush()

        var_toilet_seat = Variant(
            product_id=prod_hindware_seat.id,
            SKU="TS-WH-HW-02",
            price=8500.0,
            dimensions="22x14x14 inch",
            color="Star White",
            finish="Gloss Ceramic",
            quantity=0.0,
            reorder_threshold=2.0,
            unit="pieces",
            attributes={"trap_type": "P-Trap", "flush_type": "Dual Syphon"}
        )
        db.add(var_toilet_seat)
        db.flush()

        # Category D: Kitchen Appliances
        cat_kitchen = Category(name="Kitchen Appliances", description="Auto-clean chimneys, built-in cooktops, and sinks.")
        db.add(cat_kitchen)
        db.flush()

        sub_chimneys = Subcategory(category_id=cat_kitchen.id, name="Chimneys", description="Suction chimneys with filterless auto-clean technology.")
        db.add_all([sub_chimneys])
        db.flush()

        prod_faber_hood = Product(subcategory_id=sub_chimneys.id, name="Faber Hood Auto Clean", description="Faber 90cm 1500 m3/h Filterless Chimney.")
        db.add(prod_faber_hood)
        db.flush()

        var_chimney = Variant(
            product_id=prod_faber_hood.id,
            SKU="KA-AC-FB-90",
            price=16500.0,
            dimensions="90 cm",
            color="Black",
            finish="Tempered Glass & Steel",
            quantity=0.0,
            reorder_threshold=1.0,
            unit="pieces",
            attributes={"suction_m3h": 1500, "control_type": "Gesture & Touch"}
        )
        db.add(var_chimney)
        db.flush()

        # Category E: Plumbing
        cat_plumbing = Category(name="Plumbing", description="Heavy PVC and CPVC pipes, couplings, and valves.")
        db.add(cat_plumbing)
        db.flush()

        sub_pvc_pipes = Subcategory(category_id=cat_plumbing.id, name="PVC Pipes & Fittings", description="Conduit pipes and standard plumbing couplers.")
        db.add_all([sub_pvc_pipes])
        db.flush()

        prod_supreme_pipe = Product(subcategory_id=sub_pvc_pipes.id, name="Supreme PVC Conduit", description="Supreme heavy-duty PVC rigid electrical/plumbing conduit.")
        db.add(prod_supreme_pipe)
        db.flush()

        var_pvc_pipe = Variant(
            product_id=prod_supreme_pipe.id,
            SKU="PL-PP-SP-410",
            price=45.0, # ₹45 per meter
            dimensions="4-inch Diameter (10m Length)",
            color="Gray",
            finish="Smooth PVC",
            quantity=0.0,
            reorder_threshold=20.0,
            unit="meters",
            attributes={"pressure_rating": "PN10", "material": "UPVC"}
        )
        db.add(var_pvc_pipe)
        db.flush()

        # Category F: Electrical Items
        cat_electrical = Category(name="Electrical Items", description="Premium house copper wiring, switches, and breakers.")
        db.add(cat_electrical)
        db.flush()

        sub_wiring = Subcategory(category_id=cat_electrical.id, name="Cables & Wires", description="Flame retardant copper wiring bundles.")
        db.add_all([sub_wiring])
        db.flush()

        prod_finolex_cable = Product(subcategory_id=sub_wiring.id, name="Finolex Copper Cable", description="Finolex 2.5 sq mm multi-strand copper wire box.")
        db.add(prod_finolex_cable)
        db.flush()

        var_finolex_wire = Variant(
            product_id=prod_finolex_cable.id,
            SKU="EL-CW-FL-25",
            price=1800.0, # Per box
            dimensions="90m box",
            color="Red",
            finish="PVC Insulation",
            quantity=0.0,
            reorder_threshold=5.0,
            unit="boxes",
            attributes={"cross_section_sqmm": 2.5, "cores": 1, "fire_retardant": "FR-LSH"}
        )
        db.add(var_finolex_wire)
        db.flush()

        # Category G: Hardware Accessories
        cat_hardware = Category(name="Hardware Accessories", description="Stainless steel pulls, cabinet knobs, hinges, and fasteners.")
        db.add(cat_hardware)
        db.flush()

        sub_handles = Subcategory(category_id=cat_hardware.id, name="Cabinet Handles & Pulls", description="Solid stainless steel handles for doors and cabinets.")
        db.add_all([sub_handles])
        db.flush()

        prod_godrej_pull = Product(subcategory_id=sub_handles.id, name="Godrej Pull Handle", description="Godrej stainless steel rust-free pull handle.")
        db.add(prod_godrej_pull)
        db.flush()

        var_handle = Variant(
            product_id=prod_godrej_pull.id,
            SKU="HA-CH-GJ-06",
            price=250.0,
            dimensions="6 inch length",
            color="Satin Silver",
            finish="Brushed Stainless Steel",
            quantity=0.0,
            reorder_threshold=15.0,
            unit="pieces",
            attributes={"grade": "SS 304", "screws_included": True}
        )
        db.add(var_handle)
        db.flush()
        logger.info("Initialized 7 hardware categories, subcategories, products, and unique SKU variants.")

        # 3. Create Suppliers & Orders (To mock initial stock creation)
        sup_kajaria = Supplier(name="Kajaria Ceramics Ltd.", contact_person="Ramesh Patel", phone="9898012345", email="orders@kajaria.com", address="Sikandrabad Plant, UP")
        sup_jaquar = Supplier(name="Jaquar India Group", contact_person="Sanjay Mehta", phone="9988776655", email="support@jaquar.com", address="Manesar Head Office, Gurgaon")
        sup_supreme = Supplier(name="Supreme Pipes & Plastics", contact_person="Vijay Kapoor", phone="9090123456", email="dealers@supreme.com", address="Andheri East, Mumbai")
        sup_hindware = Supplier(name="Hindware Sanitaryware", contact_person="Deepak Sen", phone="9871112233", email="dispatch@hindware.com", address="Bahadurgarh Ceramic District, Haryana")
        sup_faber = Supplier(name="Faber Kitchen Systems", contact_person="Amit Khanna", phone="9112233445", email="b2b@faber.com", address="Pune Plant, Maharashtra")
        db.add_all([sup_kajaria, sup_jaquar, sup_supreme, sup_hindware, sup_faber])
        db.flush()
        logger.info("Added 5 production-grade suppliers.")

        # 4. Generate stock counts through transactions (to mock realistic transaction logs)
        # Order 1 (Received): Replenish White Matte Tiles, Oak Brown Tiles, Taps, supreme conduit
        po_kajaria = SupplierOrder(supplier_id=sup_kajaria.id, expected_delivery=datetime.utcnow() - timedelta(days=5), status="Received", notes="Initial stock setup for tiles")
        db.add(po_kajaria)
        db.flush()
        
        item_tiles_1 = SupplierOrderItem(supplier_order_id=po_kajaria.id, variant_id=var_white_matte.id, quantity_ordered=500.0)
        item_tiles_2 = SupplierOrderItem(supplier_order_id=po_kajaria.id, variant_id=var_oak_brown.id, quantity_ordered=300.0)
        db.add_all([item_tiles_1, item_tiles_2])
        
        # Apply transactions for received order
        tx_tiles_1 = InventoryTransaction(variant_id=var_white_matte.id, quantity=500.0, action_type="added", user_id=admin_user.id, notes="Received from Kajaria PO")
        tx_tiles_2 = InventoryTransaction(variant_id=var_oak_brown.id, quantity=300.0, action_type="added", user_id=admin_user.id, notes="Received from Kajaria PO")
        var_white_matte.quantity += 500.0
        var_oak_brown.quantity += 300.0
        db.add_all([tx_tiles_1, tx_tiles_2, var_white_matte, var_oak_brown])
        db.flush()

        # PO 2: Hindware & Jaquar Stocking
        po_sanitary = SupplierOrder(supplier_id=sup_hindware.id, expected_delivery=datetime.utcnow() - timedelta(days=2), status="Received", notes="Basin taps and water closet initial stock")
        db.add(po_sanitary)
        db.flush()

        item_taps = SupplierOrderItem(supplier_order_id=po_sanitary.id, variant_id=var_jaquar_tap.id, quantity_ordered=15.0)
        item_toilets = SupplierOrderItem(supplier_order_id=po_sanitary.id, variant_id=var_toilet_seat.id, quantity_ordered=8.0)
        db.add_all([item_taps, item_toilets])
        
        tx_taps = InventoryTransaction(variant_id=var_jaquar_tap.id, quantity=15.0, action_type="added", user_id=admin_user.id, notes="Received Hindware/Jaquar consignment")
        tx_toilets = InventoryTransaction(variant_id=var_toilet_seat.id, quantity=8.0, action_type="added", user_id=admin_user.id, notes="Received Hindware/Jaquar consignment")
        var_jaquar_tap.quantity += 15.0
        var_toilet_seat.quantity += 8.0
        db.add_all([tx_taps, tx_toilets, var_jaquar_tap, var_toilet_seat])
        db.flush()

        # Add rest of the stock
        var_chimney.quantity = 4.0
        tx_chimney = InventoryTransaction(variant_id=var_chimney.id, quantity=4.0, action_type="added", user_id=admin_user.id, notes="Manual opening stock logging")
        
        var_pvc_pipe.quantity = 150.0
        tx_pvc = InventoryTransaction(variant_id=var_pvc_pipe.id, quantity=150.0, action_type="added", user_id=admin_user.id, notes="Manual opening stock logging")
        
        var_finolex_wire.quantity = 25.0
        tx_wire = InventoryTransaction(variant_id=var_finolex_wire.id, quantity=25.0, action_type="added", user_id=admin_user.id, notes="Manual opening stock logging")
        
        # NOTE: cabinet handles HA-CH-GJ-06 will start with zero stock to intentionally trigger a low-stock alert on startup!
        var_handle.quantity = 0.0
        
        db.add_all([var_chimney, tx_chimney, var_pvc_pipe, tx_pvc, var_finolex_wire, tx_wire, var_handle])
        db.flush()
        logger.info("Stock balances created successfully. SKU HA-CH-GJ-06 started with 0.0 units to trigger reorder alerts.")

        # Trigger startup low stock alerts
        alert_handle = Alert(
            variant_id=var_handle.id,
            alert_type="low_stock",
            message=f"Stock for variant SKU HA-CH-GJ-06 (6 inch length Satin Silver) is low: 0.0 pieces left. Threshold is 15.0."
        )
        db.add(alert_handle)
        db.flush()

        # Log damaged stock event
        tx_damaged_tiles = InventoryTransaction(
            variant_id=var_white_matte.id,
            quantity=-16.0, # 1 box broken
            action_type="damaged",
            user_id=employee_user.id,
            notes="1 full box dropped by worker in loading dock, tiles cracked."
        )
        var_white_matte.quantity -= 16.0
        db.add_all([tx_damaged_tiles, var_white_matte])
        db.flush()
        logger.info("Logged broken tiles event (damaged transaction).")

        # 5. Create Sample Customers
        cust_sharma = Customer(name="Sharma Family", phone="9876543210", email="rajesh.sharma@gmail.com", notes="Regular VIP clients building a three-story residence in Vasant Kunj.")
        cust_verma = Customer(name="Verma Residency", phone="9812345678", email="anjali.verma@yahoo.com", notes="Duplex farmhouse construction in Chhatarpur.")
        db.add_all([cust_sharma, cust_verma])
        db.flush()
        logger.info("Seeded 2 sample customer accounts.")

        # 6. Create Job Projects & Assign/Consume Materials
        # Job A: Sharma Bathroom Renovation
        job_bathroom = Job(
            customer_id=cust_sharma.id,
            name="Bathroom Renovation",
            status="In_Progress",
            start_date=datetime.utcnow() - timedelta(days=10),
            deadline=datetime.utcnow() + timedelta(days=15),
            assigned_employee_id=employee_user.id,
            notes="Master guest bathroom setup with white matte wall layout and luxury brass mixers."
        )
        db.add(job_bathroom)
        db.flush()

        # Assign materials to Sharma Bathroom
        # Assign 100 sq ft white matte wall tiles, and consume 80 sq ft so far
        mat_tiles_sharma = JobMaterial(
            job_id=job_bathroom.id,
            variant_id=var_white_matte.id,
            quantity_assigned=100.0,
            quantity_consumed=80.0,
            status="Assigned"
        )
        tx_job_tiles = InventoryTransaction(
            variant_id=var_white_matte.id,
            quantity=-100.0,
            action_type="job_used",
            user_id=employee_user.id,
            notes="Assigned 100 sq ft to Rajesh Sharma Bathroom project."
        )
        var_white_matte.quantity -= 100.0
        
        # Assign 2 Jaquar Basin Mixer taps
        mat_tap_sharma = JobMaterial(
            job_id=job_bathroom.id,
            variant_id=var_jaquar_tap.id,
            quantity_assigned=2.0,
            quantity_consumed=2.0,
            status="Consumed" # fully consumed
        )
        tx_job_taps = InventoryTransaction(
            variant_id=var_jaquar_tap.id,
            quantity=-2.0,
            action_type="job_used",
            user_id=employee_user.id,
            notes="Assigned 2 mixers to Rajesh Sharma Bathroom project."
        )
        var_jaquar_tap.quantity -= 2.0
        
        db.add_all([job_bathroom, mat_tiles_sharma, tx_job_tiles, mat_tap_sharma, tx_job_taps, var_white_matte, var_jaquar_tap])
        db.flush()

        # Job B: Sharma Kitchen Setup (Pending status)
        job_kitchen = Job(
            customer_id=cust_sharma.id,
            name="Kitchen Setup",
            status="Pending",
            start_date=None,
            deadline=datetime.utcnow() + timedelta(days=40),
            assigned_employee_id=None,
            notes="Modular kitchen alignment requiring chimneys and cabinet hardware handles."
        )
        db.add(job_kitchen)
        db.flush()
        logger.info("Configured active job 'Bathroom Renovation' and pending 'Kitchen Setup' for Rajesh Sharma.")

        # Job C: Verma Outdoor Tiling (Completed status)
        job_verma_tiling = Job(
            customer_id=cust_verma.id,
            name="Outdoor Tiling",
            status="Completed",
            start_date=datetime.utcnow() - timedelta(days=20),
            deadline=datetime.utcnow() - timedelta(days=2),
            assigned_employee_id=employee_user.id,
            notes="Front porch anti-skid somany wood plank tiling. Finished successfully."
        )
        db.add(job_verma_tiling)
        db.flush()

        # Assign and consume 150 sq ft somany planks
        mat_verma_tiles = JobMaterial(
            job_id=job_verma_tiling.id,
            variant_id=var_oak_brown.id,
            quantity_assigned=150.0,
            quantity_consumed=150.0,
            status="Consumed"
        )
        tx_verma_tiles = InventoryTransaction(
            variant_id=var_oak_brown.id,
            quantity=-150.0,
            action_type="job_used",
            user_id=employee_user.id,
            notes="Assigned and installed 150 sq ft at Verma farm porch."
        )
        var_oak_brown.quantity -= 150.0
        db.add_all([job_verma_tiling, mat_verma_tiles, tx_verma_tiles, var_oak_brown])
        db.flush()
        logger.info("Created and closed completed job 'Outdoor Tiling' for Verma residency.")

        # 7. Create a Pending Supplier purchase order from Faber Chimneys to display on the dashboard!
        po_faber = SupplierOrder(
            supplier_id=sup_faber.id,
            order_date=datetime.utcnow() - timedelta(days=1),
            expected_delivery=datetime.utcnow() + timedelta(days=4),
            status="Pending",
            notes="Reordering 5 chimneys for kitchen appliances stocks"
        )
        db.add(po_faber)
        db.flush()
        
        po_item_chimney = SupplierOrderItem(
            supplier_order_id=po_faber.id,
            variant_id=var_chimney.id,
            quantity_ordered=5.0
        )
        db.add(po_item_chimney)
        db.flush()
        logger.info("Added pending PO order from Faber for chimney restock tracking.")

        # 8. Create historical Audit Log entries
        log1 = AuditLog(user_id=admin_user.id, action="Established system database schema and seed profiles", target_type="user", target_id=admin_user.id, details={"status": "complete"})
        log2 = AuditLog(user_id=admin_user.id, action="Logged opening consignment from Kajaria Ceramics", target_type="order", target_id=po_kajaria.id, details={"supplier": "Kajaria", "consignment_value": "large"})
        log3 = AuditLog(user_id=employee_user.id, action="Logged broken white ceramic box in warehouse dock", target_type="variant", target_id=var_white_matte.id, details={"sku": "TI-WM-KM-2X2", "loss": 16.0})
        log4 = AuditLog(user_id=employee_user.id, action="Allocated materials to Sharma Bathroom Renovation", target_type="job", target_id=job_bathroom.id, details={"assigned_sku": "TI-WM-KM-2X2"})
        log5 = AuditLog(user_id=None, action="Low stock alert triggered", target_type="alert", target_id=alert_handle.id, details={"sku": "HA-CH-GJ-06"})
        db.add_all([log1, log2, log3, log4, log5])
        
        db.commit()
        logger.info("Database seeding successfully completed with 100% realistic datasets.")

    except Exception as e:
        db.rollback()
        logger.exception("An error occurred during database seeding:")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
