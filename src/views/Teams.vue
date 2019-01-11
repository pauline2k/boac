<template>
<div class="all-cohorts-container">
    <Spinner/>
    <div v-if="!loading">
      <h1 class="page-section-header">Teams</h1>
      <div v-if="!size(teams)">
        <div>No teams available</div>
      </div>
      <div v-if="size(teams)">
        <ul class="home-list">
          <li v-for="team in teams">
            <router-link :to="team.url">{{ team.name }}</router-link>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import _ from 'lodash';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import Util from '@/mixins/Util';
import { getTeamGroups } from '@/api/student';

export default {
  name: 'Teams',
  mixins: [Loading, Util],
  components: {
     Spinner
  },
  mounted() {
    this.loadTeams();
  },
  data: () => ({
    teams: []
  }),
  methods: {
    loadTeams() {
      const teams = {};
      getTeamGroups().then(data => {
        _.each(data, t => {
          const teamCode = t.teamCode;
          if (!teams[teamCode]) {
            const teamName = t.teamName;
            teams[teamCode] = {
              code: t.teamCode,
              name: teamName,
              url: '/cohort?name=' + encodeURI(teamName) + '&',
              teamGroups: []
            };
          }
          teams[teamCode].url += 'team=' + encodeURI(t.groupCode) + '&';
        });
	      this.teams = _.values(teams);
        this.loaded();
      });
    }
  }
};
</script>
