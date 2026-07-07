<template>
  <!-- Main Overlay Drawer -->
  <div
    class="fixed inset-y-0 right-0 z-50 w-full sm:w-[450px] bg-white border-l border-industrial-200 shadow-2xl flex flex-col transform transition-transform duration-300 ease-in-out"
    :class="chatStore.isOpen ? 'translate-x-0' : 'translate-x-full'"
  >
    <!-- Drawer Header -->
    <div class="bg-industrial-800 text-white p-4 flex items-center justify-between border-b border-industrial-900 shadow-sm">
      <div class="flex items-center gap-2">
        <Bot class="w-6 h-6 text-steel-400 animate-pulse" />
        <div>
          <h2 class="font-bold text-lg leading-tight font-sans tracking-wide">AI Store Assistant</h2>
          <span class="text-xs text-industrial-300">Powered by Gemini 1.5 Flash</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="chatStore.clearHistory"
          title="Clear Conversation"
          class="p-1.5 hover:bg-industrial-700 rounded transition-colors text-industrial-300 hover:text-white"
        >
          <Trash2 class="w-4 h-4" />
        </button>
        <button
          @click="chatStore.setSidebarOpen(false)"
          class="p-1.5 hover:bg-industrial-700 rounded transition-colors text-industrial-300 hover:text-white"
        >
          <X class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Chat Messages Log -->
    <div ref="chatLog" class="flex-1 overflow-y-auto p-4 space-y-4 bg-industrial-50">
      <div
        v-for="(msg, index) in chatStore.messages"
        :key="index"
        class="flex flex-col max-w-[85%]"
        :class="msg.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'"
      >
        <span class="text-[10px] text-industrial-400 mb-1 px-1">
          {{ msg.role === 'user' ? 'You' : 'AI Assistant' }}
        </span>
        <div
          class="p-3 rounded-2xl shadow-sm text-sm leading-relaxed whitespace-pre-line font-sans"
          :class="
            msg.role === 'user'
              ? 'bg-steel-600 text-white rounded-tr-none'
              : 'bg-white text-industrial-800 border border-industrial-200/80 rounded-tl-none'
          "
        >
          <!-- Direct Render or formatted summary -->
          {{ msg.content }}
        </div>
      </div>

      <!-- Loading / Thinking Indicator -->
      <div v-if="chatStore.loading" class="flex flex-col mr-auto max-w-[85%] items-start">
        <span class="text-[10px] text-industrial-400 mb-1 px-1">AI Assistant</span>
        <div class="p-3 bg-white border border-industrial-200/80 rounded-2xl rounded-tl-none flex items-center gap-2">
          <div class="flex space-x-1">
            <div class="w-2.5 h-2.5 bg-steel-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2.5 h-2.5 bg-steel-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2.5 h-2.5 bg-steel-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
          </div>
          <span class="text-xs text-industrial-500 font-medium">Consulting backend tools...</span>
        </div>
      </div>
    </div>

    <!-- Message Input Box -->
    <div class="p-3 border-t border-industrial-200 bg-white">
      <form @submit.prevent="submitQuery" class="flex gap-2">
        <input
          v-model="inputQuery"
          type="text"
          placeholder="Ask about stock levels, jobs, or summaries..."
          class="flex-1 px-3 py-2 text-sm border border-industrial-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 bg-industrial-50"
          :disabled="chatStore.loading"
        />
        <button
          type="submit"
          class="bg-steel-600 hover:bg-steel-700 active:scale-95 text-white px-4 py-2 rounded-xl transition-all flex items-center justify-center disabled:opacity-50"
          :disabled="chatStore.loading || !inputQuery.trim()"
        >
          <Send class="w-4 h-4" />
        </button>
      </form>
      <div class="text-[10px] text-industrial-400 text-center mt-2">
        Type "low stock" or SKU code to instantly test backend service calls.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { useChatStore } from '../store/chat';
import { Bot, Trash2, X, Send } from 'lucide-vue-next';

const chatStore = useChatStore();
const inputQuery = ref('');
const chatLog = ref(null);

const scrollToBottom = async () => {
  await nextTick();
  if (chatLog.value) {
    chatLog.value.scrollTop = chatLog.value.scrollHeight;
  }
};

// Scroll on new message arrivals
watch(
  () => chatStore.messages.length,
  () => {
    scrollToBottom();
  }
);

// Scroll when side drawer pops open
watch(
  () => chatStore.isOpen,
  (open) => {
    if (open) {
      scrollToBottom();
    }
  }
);

const submitQuery = async () => {
  const text = inputQuery.value.trim();
  if (!text) return;

  inputQuery.value = '';
  await chatStore.sendQuery(text);
};
</script>
