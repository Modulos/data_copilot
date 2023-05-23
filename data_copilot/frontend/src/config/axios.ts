import type { AxiosInstance } from 'axios';
import { useAuthStore } from '@/stores/auth';
import useMessagesStore from '@/stores/messages';
import useChatsStore from '@/stores/chats';

function defineInterceptors(axios: AxiosInstance) {
  const messages = useMessagesStore();
  const chats = useChatsStore();
  const auth = useAuthStore();

  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.code === 'ERR_NETWORK' || error.response.status === 500) {
        auth.serviceDown();
      }

      if (error.response.status === 401) {
        messages.clearMessages();
        chats.clearActiveChat();
        auth.logout();
      }

      return Promise.reject(error);
    },
  );
}

export default defineInterceptors;
