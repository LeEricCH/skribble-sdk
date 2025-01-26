module.exports = {
  extends: ["@repo/eslint-config/library.js"],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    project: "./tsconfig.json",
    tsconfigRootDir: __dirname,
  },
  env: {
    jest: true,
    node: true
  },
  rules: {
    "@typescript-eslint/no-explicit-any": "warn"
  }
}; 