/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  distDir: 'out',
  basePath: '/interactive',
  assetPrefix: '/interactive',
}

module.exports = nextConfig
