import globals from "globals";
import pluginJs from "@eslint/js";
import pluginReact from "eslint-plugin-react";
import { parser } from "@babel/eslint-parser";

export default [
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
      parserOptions: {
        ecmaVersion: 2021,  // ECMAScript version 2021 for modern JavaScript
        sourceType: "module",  // Allows the use of imports
        ecmaFeatures: {
          jsx: true,  // Enable JSX support
        },
      },
    },
    plugins: {
      react: pluginReact, // Register the react plugin
    },
    rules: {
      "react/react-in-jsx-scope": "off", // Disable the rule for React 17+
      "react/prop-types": "off", // Optionally disable prop-types rule (if using TypeScript or don't need it)
      "no-unused-vars": "warn", // Show warnings for unused variables
    },
  },
  pluginJs.configs.recommended,
  pluginReact.configs.flat.recommended,
];