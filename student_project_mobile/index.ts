// index.ts
import { registerRootComponent } from "expo";
import App from "./App";

/**
 * This registers the main App component as the root component of the Expo app.
 * Expo will take care of loading, rendering, and hot reloading.
 * 
 * Do NOT import this index.ts anywhere else, especially not in App.tsx.
 */
registerRootComponent(App);
