const HtmlWebpackPlugin = require("html-webpack-plugin");
const path = require("path");

module.exports = {
  mode: "development",
  entry: { index: path.resolve(__dirname, "src/main", "index.js") },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: ["babel-loader"],
      },
    ],
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, "src/main", "index.html"),
    }),
    new HtmlWebpackPlugin({
      filename: "dashboard.html",
      template: path.resolve(__dirname, "src/main", "dashboard.html"),
    }),
  ],
  devServer: {
    compress: true,
    hot: true,
    port: 8080,
  },
};
