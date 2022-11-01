const defaultTheme = require("tailwindcss/defaultTheme");

// const fontFamily = defaultTheme.fontFamily;
// fontFamily["sans"] = [
//     "Inter", // <-- Roboto is a default sans font now
//     "system-ui",
//     // <-- you may provide more font fallbacks here
// ];

module.exports = {
  content: [
    /**
     * HTML. Paths to Django template files that will contain Tailwind CSS classes.
     */

    /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
    "../templates/**/*.html",

    /*
     * Main templates directory of the project (BASE_DIR/templates).
     * Adjust the following line to match your project structure.
     */
    "../../templates/**/*.html",

    /*
     * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
     * Adjust the following line to match your project structure.
     */
    "../../**/templates/**/*.html",

    /**
     * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
     * patterns match your project structure.
     */
    /* JS 1: Ignore any JavaScript in node_modules folder. */
    // '!../../**/node_modules',
    /* JS 2: Process all JavaScript files in the project. */
    // '../../**/*.js',

    /**
     * Python: If you use Tailwind CSS classes in Python, uncomment the following line
     * and make sure the pattern below matches your project structure.
     */
    // '../../**/*.py'
    "./node_modules/flowbite/**/*.js",
  ],
  theme: {
    // fontFamily: fontFamily,
    fontFamily: {
      sans: ["Inter", "system-ui"],
      // sans: ["ui-monospace", "SFMono-Regular"],
      montserrat: ["Montserrat", "sans-serif"],
    },
    extend: {
      animation: {
        blob: "blob 7s infinite",
        fadeIn: "fadeIn 2s forwards",
      },
      keyframes: {
        blob: {
          "0%": {
            transform: "translate(0px, 0px) scale(1) rotate(12)",
          },
          "33%": {
            transform: "translate(30px, -50px) scale(1.1)",
          },
          "66%": {
            transform: "translate(-20px, 20px) scale(0.9) rotate(-24)",
          },
          "100%": {
            transform: "tranlate(0px, 0px) scale(1)",
          },
        },
        fadeIn: {
          "0%": { opacity: 0 },
          "100%": { opacity: 1 },
        },
      },
    },
  },
  variants: {
    // animation: ["motion-safe"],
    extend: {},
  },
  plugins: [
    /**
     * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
     * for forms. If you don't like it or have own styling for forms,
     * comment the line below to disable '@tailwindcss/forms'.
     */
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/line-clamp"),
    require("@tailwindcss/aspect-ratio"),
    require("tailwindcss-animation-delay"),
  ],
};
