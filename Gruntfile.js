module.exports = function(grunt) {
  grunt.initConfig({
    browserSync: {
      dev: {
        bsFiles: {
          src: [
            'saleor/static/css/*.css',
            'saleor/static/js/*.js',
            'saleor/**/*.html'
          ]
        },
        options: {
          open: false,
          port: "3004",
          proxy: "localhost:8000",
          watchTask: true
        }
      }
    },
    copy: {
      production: {
        files: [
          {
            expand: true,
            dot: true,
            cwd: "saleor/static/components/bootstrap/dist/js/",
            dest: "saleor/static/dist/js/",
            src: [
              "bootstrap.min.js"
            ]
          },
          {
            expand: true,
            dot: true,
            cwd: "saleor/static/components/bootstrap/fonts",
            dest: "saleor/static/dist/fonts/",
            src: [
              "*"
            ]
          },
          {
            expand: true,
            dot: true,
            cwd: "saleor/static/components/components-font-awesome/fonts",
            dest: "saleor/static/dist/fonts/",
            src: [
              "*"
            ]
          },
          {
            expand: true,
            dot: true,
            cwd: "saleor/static/components/materialize/font/roboto",
            dest: "saleor/static/dist/fonts/",
            src: [
              "*"
            ]
          },
          {
            expand: true,
            dot: true,
            cwd: "saleor/static/components/materialize/font/material-design-icons",
            dest: "saleor/static/dist/fonts/",
            src: [
              "*"
            ]
          },
          {
            expand: true,
            dot: true,
            cwd: "saleor/static/components/zocial-less/css",
            dest: "saleor/static/dist/fonts/",
            src: [
              "zocial-regular-*"
            ]
          },
          {
            expand: true,
            dot: true,
            cwd: "saleor/static/components/less/dist/",
            dest: "saleor/static/dist/js/",
            src: [
              "less.min.js"
            ]
          },
          {
            expand: true,
            dot: true,
            cwd: "saleor/static/components/jquery/dist/",
            dest: "saleor/static/dist/js/",
            src: [
              "jquery.min.*"
            ]
          }
        ]
      }
    },
    less: {
      production: {
        options: {
          compress: true,
          yuicompress: true,
          cleancss: true,
          optimization: 2
        },
        files: {
          "saleor/static/css/style.css": "saleor/static/less/style.less",
          "saleor/static/css/dashboard.css": "saleor/static/less/dashboard.less"
        }
      }
    },
    postcss: {
      options: {
        map: true,
        processors: [
          require('autoprefixer-core'),
          require('csswring')
        ]
      },
      prod: {
        src: "saleor/static/css/dashboard.css"
      }
    },
    sass: {
      options: {
        sourceMap: true,
        includePaths: ["saleor/static/components"]
      },
      dist: {
        files: {
          "saleor/static/css/dashboard.css": "saleor/static/scss/dashboard.scss"
        }
      }
    },
    uglify: {
      options: {
        mangle: false,
        sourceMap: true
      },
      dev: {
        files: {
          "saleor/static/js/dashboard.js": [
            "saleor/static/components/jquery/dist/jquery.js",
            "saleor/static/components/materialize/dist/js/materialize.js",
            "saleor/static/js_src/dashboard.js"
          ]
        }
      }
    },
    watch: {
      options: {
        atBegin: true,
        interrupt: false,
        livereload: true,
        spawn: false
      },
      sass: {
        files: ["saleor/static/scss/**/*.scss"],
        tasks: ["sass", "postcss"]
      },
      uglify: {
        files: ["saleor/static/js/**/*.js"],
        tasks: ["uglify"]
      },
      html: {
        files: ["saleor/dashboard/**/*.html"],
        tasks: []
      }
    }
  });

  grunt.loadNpmTasks("grunt-browser-sync");
  grunt.loadNpmTasks("grunt-contrib-copy");
  grunt.loadNpmTasks("grunt-contrib-less");
  grunt.loadNpmTasks("grunt-contrib-uglify");
  grunt.loadNpmTasks("grunt-contrib-watch");
  grunt.loadNpmTasks("grunt-postcss");
  grunt.loadNpmTasks("grunt-sass");

  grunt.registerTask("default", ["copy", "less", "sass", "postcss", "uglify"]);
  grunt.registerTask("sync", ["browserSync", "watch"]);
  grunt.registerTask("heroku", ["copy", "less", "sass", "postcss", "uglify"]);
};
