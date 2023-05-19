/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
import { defineStore } from 'pinia';
import initApi from '@/client_helpers/utils';
import router from '../router';
import type { Message } from '../client/api';

import { ChatApi } from '../client/api';

interface State {
  messages: Message[];
  inputDisabled: boolean;
  isLoading: boolean;
  activeTimoutId: ReturnType<typeof setTimeout> | null;
  isLoadingMessages: boolean;
  messagesCount: number;
  limit: number;
  offset: number;
}

const useMessagesStore = defineStore({
  id: 'messages',
  state: (): State => ({
    messages: [],
    inputDisabled: false,
    activeTimoutId: null,
    isLoading: false,
    isLoadingMessages: false,
    messagesCount: 0,
    limit: 20,
    offset: 0,
  }),
  getters: {
    hasMessages(state) {
      return state.messages.length > 0;
    },
    notAllowedNexLoad(state) {
      return (
        state.messagesCount - state.offset < 0 || state.isLoadingMessages
      );
    },
  },
  actions: {
    clearMessages() {
      this.messages = [];
      this.removeTimeout();
    },
    async firstMessage(chat_id: string, message: string) {
      const chatApi = initApi(ChatApi);
      const m = await chatApi.postChatsChatidMessagesApiChatsChatIdMessagesPost(
        chat_id,
        message,
      );
      this.messages.push(m.data);
    },
    async getMessages(chat_id: string) {
      try {
        this.offset = 0;
        this.isLoading = true;
        const chatApi = initApi(ChatApi);
        const responseMessages = await chatApi.getChatsChatidMessagesApiChatsChatIdMessagesGet(
          chat_id,
          this.limit,
          this.offset,
        );
        this.messages = responseMessages.data.data.reverse();

        this.messagesCount = responseMessages.data.metadata.total;
        this.offset += this.limit;
      } catch (error: any) {
        if (error.response && error.response.status === 404) {
          router.push('/not-found');
        }
        console.error(error);
      } finally {
        this.isLoading = false;
        this.inputDisabled = false;
      }
      // const lastMessage =
      //   responseMessages.data[responseMessages.data.length - 1];
      // const from_date = lastMessage.created_at;

      // this.longPolling(chat_id, {
      //   fromDate: fromDate,
      //   limit: 20,
      //   offset: 0,
      //   polling: true,
      // });
    },

    async loadMoreMessages(chat_id: string) {
      const chatApi = initApi(ChatApi);

      if (this.notAllowedNexLoad) return;

      try {
        this.isLoadingMessages = true;

        const response = await chatApi.getChatsChatidMessagesApiChatsChatIdMessagesGet(
          chat_id,
          this.limit,
          this.offset,
        );
        this.messages = response.data.data.reverse().concat(this.messages);
        this.offset += this.limit;
      } catch (error) {
        console.log(error);
      } finally {
        this.isLoadingMessages = false;
      }
    },

    async longPolling(chat_id: string, options = {}) {
      const {
        limit, offset, fromDate, toDate, polling,
      } = {
        limit: undefined,
        offset: undefined,
        fromDate: undefined,
        toDate: undefined,
        polling: undefined,
        ...options,
      };

      const chatApi = initApi(ChatApi);
      const response = await chatApi.getChatsChatidMessagesApiChatsChatIdMessagesGet(
        chat_id,
        limit,
        offset,
        fromDate,
        toDate,
        polling,
      );

      if (response.status === 502) {
        // Status 502 is a connection timeout error,
        // may happen when the connection was pending for too long,
        // and the remote server or a proxy closed it
        // let's reconnect
        // this.longPolling(chat_id, { ...options });
      } else if (response.status !== 200) {
        // An error - let's show it
        // Reconnect in one second
        await this.wait(1000);
        // this.longPolling(chat_id, { ...options });
      } else {
        // Get and show the message
        let lastMessage;
        let createdDate;

        if (response.data.data.length > 0) {
          if (this.activeTimoutId) {
            this.removeTimeout();
          }
          this.inputDisabled = false;
          // lastMessage = response.data[response.data.length - 1];
          // from_date = lastMessage.created_at;

          for (let i = 0; i < response.data.data.length; i += 1) {
            const lastId = this.messages[this.messages.length - 1].id;
            if (response.data.data[i].id !== lastId) {
              this.messages.push(response.data.data[i]);
            }
          }
        }

        // Call subscribe() again to get the next message
        // this.longPolling(chat_id, {
        //   ...options,
        //   fromDate: from_date ? from_date : fromDate,
        // });
      }
    },

    wait(ms: number) {
      return new Promise<void>((resolve) => {
        setTimeout(() => {
          resolve();
        }, ms);
      });
    },

    async postMessage(
      chat_id: string,
      message: string,
      artifactVersionId: string,
    ) {
      this.inputDisabled = true;
      this.activeTimoutId = setTimeout(() => {
        this.inputDisabled = false;
      }, 60000);
      const chatApi = initApi(ChatApi);
      const m = await chatApi.postChatsChatidMessagesApiChatsChatIdMessagesPost(
        chat_id,
        message,
        artifactVersionId,
      );
      this.messages.push(m.data);
      return m.data.id;
    },

    async executeMessage(chat_id: string, message_id: string) {
      const chatApi = initApi(ChatApi);
      await chatApi.postChatsChatidMessagesMessageidApiChatsChatIdMessagesMessageIdExecutePost(
        message_id,
        chat_id,
      );
      // if (this.messages.length === 1) {
      const m = this.messages[this.messages.length - 1];
      const fromDate = m.created_at;
      this.longPolling(chat_id, {
        fromDate: fromDate,
        limit: 20,
        offset: 0,
        polling: true,
      });
      // }
      // this.messages.push(m.data);
    },

    removeTimeout() {
      if (this.activeTimoutId) {
        clearTimeout(this.activeTimoutId);
      }
    },
  },
});

export default useMessagesStore;
