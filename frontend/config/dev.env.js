let date = require('moment')().format('YYYYMMDD')
let commit = 'dev'
try {
  // Try to get git commit hash from parent directory (root of monorepo)
  commit = require('child_process').execSync('git rev-parse HEAD', { cwd: require('path').join(__dirname, '../..') }).toString().slice(0, 5)
} catch (e) {
  // If git is not available, use 'dev' as default
  commit = 'dev'
}
let version = `"${date}-${commit}"`

console.log(`current version is ${version}`)

module.exports = {
  NODE_ENV: '"development"',
  VERSION: version,
  USE_SENTRY: '0'
}
