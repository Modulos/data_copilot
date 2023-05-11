import { useAuthStore } from '@/stores/auth';
import { Configuration } from '../client/configuration';

import router from '../router';

// TODO: how to type the api here
function initApi(Api: any) {
  const authStore = useAuthStore();
  if (authStore.accessToken === null) {
    router.push('/login');
    return null;
  }
  const baseUrl = `${import.meta.env.VITE_API_URL}`;
  const config = new Configuration();
  config.basePath = baseUrl;
  config.accessToken = '';
  config.accessToken = authStore.accessToken;
  const newApi = new Api(config);
  return newApi;
}

export default initApi;
