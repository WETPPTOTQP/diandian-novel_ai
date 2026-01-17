import { createRouter, createWebHistory } from "vue-router";
import Home from "./views/Home.vue";
import Write from "./views/Write.vue";
import Ideas from "./views/Ideas.vue";
import Profile from "./views/Profile.vue";
import Character from "./views/Character.vue";
import Style from "./views/Style.vue";

const routes = [
  { path: "/", name: "home", component: Home },
  { path: "/write/:id", name: "write", component: Write, props: true },
  { path: "/ideas", name: "ideas", component: Ideas },
  { path: "/profile", name: "profile", component: Profile },
  { path: "/character", name: "character", component: Character },
  { path: "/style", name: "style", component: Style }
];

export default createRouter({
  history: createWebHistory(),
  routes
});

