<template>
    <div :class="['message', messageClass]">
      <div class="message-content" v-html="renderedMessage"></div>
    </div>
  </template>
  
  <script>
  import markdownIt from 'markdown-it';
  
  export default {
    props: {
      message: {
        type: Object,
        required: true,
      },
    },
    computed: {
      messageClass() {
        return this.message.sender === 'user' ? 'user-message' : 'assistant-message';
      },
      renderedMessage() {
        const md = markdownIt();
        return md.render(this.message.text);
      },
    },
  };
  </script>
  
  <style scoped>
  .message {
    margin: 10px 0;
    display: flex;
  }
  .user-message {
    justify-content: flex-end;
  }
  .assistant-message {
    justify-content: flex-start;
  }
  .message-content {
    max-width: 70%;
    background-color: #2e2e2e;
    padding: 10px;
    border-radius: 8px;
    color: #fff;
    word-break: break-word;
  }
  .user-message .message-content {
    background-color: #4a4a4a;
  }
  </style>