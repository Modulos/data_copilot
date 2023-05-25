import { defineStore } from 'pinia';
// eslint-disable-next-line import/no-cycle
import router from '../router';
import { AuthenicationApi, UsersApi } from '../client/api';
import type { User } from '../client/api';
import { Configuration } from '../client/configuration';

const baseUrl = `${import.meta.env.VITE_API_URL}`;
const config = new Configuration();
config.basePath = baseUrl;
config.accessToken = '';

const authApi = new AuthenicationApi(config);
const usersApi = new UsersApi(config);

interface State {
  accessToken: string | null;
  tokenExpiresAt: number | null;
  user: User | null
  refreshTimerId: ReturnType<typeof setTimeout> | undefined;
  activateAnimation: boolean;
}

const token = localStorage.getItem('token');
const tokenExpiresAt = localStorage.getItem('tokenExpiresAt');
const me = localStorage.getItem('user');
const minutes = 1000 * 60 * 15;

export const useAuthStore = defineStore({
  id: 'auth',
  state: (): State => ({
    accessToken: token || null,
    tokenExpiresAt: tokenExpiresAt ? Number(tokenExpiresAt) : null,
    refreshTimerId: undefined,
    user: me ? JSON.parse(me) : null,
    activateAnimation: false,
  }),
  actions: {
    async login(username: string, password: string) {
      const user = await authApi.loginForAccessTokenApiTokenPost(
        username,
        password,
      );
      this.setToken(user.data.access_token);

      const response = await usersApi.getUsersMeApiUsersMeGet();
      this.user = response.data;
      localStorage.setItem('user', JSON.stringify(response.data));

      router.push('/');
    },

    async signup(
      firstName: string,
      lastName: string,
      password: string,
      email: string,
    ) {
      await usersApi.postUsersApiUsersPost(
        {
          first_name: firstName,
          last_name: lastName,
          password,
          email,
        },
      );
      await this.login(email, password);
    },
    setToken(newToken: string) {
      const date = Date.now() + minutes;
      config.accessToken = newToken;
      this.accessToken = newToken;
      this.tokenExpiresAt = date;

      localStorage.setItem('token', newToken);
      localStorage.setItem('tokenExpiresAt', date.toString());

      this.startTimer();
    },

    startTimer() {
      if (!this.tokenExpiresAt) return;
      const diff = this.tokenExpiresAt - Date.now();
      this.refreshTimerId = setTimeout(() => {
        this.refresh();
      }, diff);
    },

    stopTimer() {
      if (!this.refreshTimerId) return;

      clearTimeout(this.refreshTimerId);
      this.refreshTimerId = undefined;
    },

    async refresh() {
      const response = await authApi.refreshTokenApiTokenRefreshPost();
      console.log(response.data);

      this.setToken(response.data.access_token);
    },

    serviceDown() {
      router.push('/service-down');
    },

    logout() {
      // remove user from local storage to log user out
      localStorage.removeItem('tokenExpiresAt');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      this.tokenExpiresAt = null;
      this.accessToken = null;
      router.push('/login');
      this.stopTimer();
    },
  },
});

export default useAuthStore;
