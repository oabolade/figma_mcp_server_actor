import prettierConfig from "eslint-config-prettier";

import apifyConfig from "@apify/eslint-config";

const config = [
  ...apifyConfig,
  prettierConfig,
  {
    files: ["**/*.js", "**/*.mjs"],
    ignores: ["node_modules/**", "storage/**", "dist/**", "build/**"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
    },
  },
  {
    files: ["eslint.config.js"],
    rules: {
      "import/no-default-export": "off",
    },
  },
];

export default config;
