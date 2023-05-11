import { defineStore } from 'pinia';
import initApi from '@/client_helpers/utils';
import type { Artifact } from '../client/api';
import { ArtifactApi, ArtifactTypes } from '../client/api';

interface State {
  artifacts: Artifact[];
  artifact_id: string;
  showSnackbar: boolean;
  isLoading: boolean,
}

const useArtifactStore = defineStore({
  id: 'artifact',
  state: ():State => ({
    artifacts: [],
    artifact_id: '',
    showSnackbar: false,
    isLoading: false,
  }),
  actions: {
    async getArtifacts() {
      const artifactApi = initApi(ArtifactApi);
      const artifacts = await artifactApi.getArtifactsApiArtifactsGet();
      this.artifacts = artifacts.data;
    },
    async createArtifact(fileName: string) {
      this.isLoading = true;
      const artifactApi = initApi(ArtifactApi);
      const artifact = await artifactApi.postArtifactApiArtifactsPost(
        { name: fileName, description: fileName, artifact_type: ArtifactTypes.Dataset },
      );
      this.artifact_id = artifact.data.id;
      return this.artifact_id;
    },
    async uploadArtifact(file: File) {
      const artifactApi = initApi(ArtifactApi);
      let artifact;
      try {
        artifact = await artifactApi.postArtifactsIdArtifactidVersionsApiArtifactsArtifactIdVersionsPost(
          this.artifact_id,
          file,
        );

        if (artifact.status === 201) {
          this.showSnackbar = true;
        }
      } catch (err) {
        console.error(err);
      } finally {
        this.isLoading = false;
      }
      return artifact;
    },
  },
});

export default useArtifactStore;
