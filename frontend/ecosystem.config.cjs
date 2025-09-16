module.exports = {
  apps: [{
    name: 'frontend-dev-server',
    script: 'node',
    args: 'simple-server.cjs',
    cwd: '/home/user/webapp/frontend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development',
      PORT: 3000
    },
    log_file: './logs/combined.log',
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    time: true
  }]
}