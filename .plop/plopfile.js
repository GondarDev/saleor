const ROOT = "../saleor/static/dashboard-next";

const componentGeneratorConfig = {
  description: "New component",
  prompts: [
    {
      type: "input",
      name: "name",
      message: "Component name?"
    },
    {
      type: "input",
      name: "section",
      message: "Component path?"
    },
    {
      type: "confirm",
      name: "fc",
      message: "Is it a functional component?",
      default: "y"
    },
    {
      type: "confirm",
      name: "styled",
      message: "Is it a styled component?",
      default: "y"
    },
    {
      type: "confirm",
      name: "story",
      message: "Create story?",
      default: "y"
    }
  ],
  actions: ({ fc, story }) => {
    const actions = [
      {
        type: "add",
        path: `${ROOT}/{{ dashCase section }}/{{ properCase name }}/index.ts`,
        templateFile: './component/index.ts.hbs',
        abortOnFail: true
      },
      {
        type: "add",
        path: `${ROOT}/{{ dashCase section }}/{{ properCase name }}/{{ properCase name }}.tsx`,
        templateFile: fc
          ? "./component/componentName.fc.tsx.hbs"
          : "./component/componentName.class.tsx.hbs",
        abortOnFail: true
      },
    ];

    if (story) {
      actions.push({
        type: "add",
        path: `${ROOT}/storybook/stories/{{ dashCase section }}/{{ properCase name }}.tsx`,
        templateFile: "./component/componentName.story.tsx.hbs",
        abortOnFail: true
      });
    }

    return actions;
  }
};

const 

module.exports = plop => {
  plop.setGenerator('component', componentGeneratorConfig);
};
