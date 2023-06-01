import { defineStore } from 'pinia';
import initApi from '@/client_helpers/utils';
import useMessagesStore from '@/stores/messages';
import router from '../router';
import type { Chat } from '../client/api';
import { ChatApi, ArtifactApi } from '../client/api';

interface State {
  chats: Chat[];
  activeChat: string | null;
  activeDatasetName: string | null;
  artifactVersionId: string | null;
  isLoading: boolean;
}

const useChatsStore = defineStore({
  id: 'chats',
  state: (): State => ({
    chats: [],
    activeChat: null,
    activeDatasetName: null,
    artifactVersionId: null,
    isLoading: false,
  }),
  getters: {
    hasChats(state) {
      return state.chats.length > 0;
    },
    hasActiveChat(state) {
      return state.activeChat !== null && state.activeDatasetName !== null;
    },
  },
  actions: {
    async clearChats() {
      const chatApi = initApi(ChatApi);
      await chatApi.deleteChatsApiChatsDelete();

      this.chats = [];
      this.clearActiveChat();
    },
    clearActiveChat() {
      this.activeChat = null;
      this.activeDatasetName = null;
      this.artifactVersionId = null;
    },
    async createChat(artifact_id: string, file_name: string) {
      const chatApi = initApi(ChatApi);

      const chat = await chatApi.createChatApiChatsPost(artifact_id, file_name);

      this.chats.unshift(chat.data);
      this.activeChat = chat.data.id;
      return chat.data.id;
    },
    async deleteChat(chatId:string) {
      const messageStore = useMessagesStore();
      const chatApi = initApi(ChatApi);
      await chatApi.deleteChatChatidApiChatsChatIdDelete(chatId);

      if (this.activeChat === chatId) {
        messageStore.messages = [];
        this.clearActiveChat();
        router.push('/');
      }
      this.chats = this.chats.filter((obj) => obj.id !== chatId);
    },
    async editChat(chatId:string, chatName: string) {
      const chatApi = initApi(ChatApi);
      await chatApi.patchChatChatidApiChatsChatIdPatch(chatId, {
        name: chatName,
      });

      const editedChat = this.chats.find((obj) => obj.id === chatId);

      if (editedChat) {
        editedChat.name = chatName;
      }
    },
    async getChats() {
      const chatApi = initApi(ChatApi);
      const chats = await chatApi.getChatsApiChatsGet();
      this.chats = chats.data;
    },
    async getActiveDatasetNameAndArtifactVersion() {
      if (this.activeChat !== null) {
        const activeChat = this.chats.find(
          (chat) => chat.id === this.activeChat,
        );
        if (activeChat) {
          const artifactApi = initApi(ArtifactApi);
          try {
            const artifact = await artifactApi.getArtifactsIdArtifactidApiArtifactsArtifactIdGet(
              activeChat.artifact_id,
            );
            this.activeDatasetName = artifact.data.name;
            const artifactVersion = await artifactApi.getArtifactsIdArtifactidVersionsApiArtifactsArtifactIdVersionsGet(
              activeChat.artifact_id,
            );

            this.artifactVersionId = artifactVersion.data[0].id;
          } catch (error) {
            this.artifactVersionId = null;
            this.activeDatasetName = 'Dataset not found';
          }
        }
      } else {
        this.activeDatasetName = 'No Dataset selected';
      }
    },
  },
});

export default useChatsStore;
