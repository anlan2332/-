// PM2 Ecosystem Configuration for BaiKaoTong AI Writing Platform

module.exports = {
  apps: [
    {
      name: 'baikao-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/app/frontend',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        HOST: '0.0.0.0'
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000,
        HOST: '0.0.0.0'
      },
      env_development: {
        NODE_ENV: 'development',
        PORT: 3000,
        HOST: '127.0.0.1'
      },
      log_file: '/app/logs/frontend-combined.log',
      out_file: '/app/logs/frontend-out.log',
      error_file: '/app/logs/frontend-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 10000
    },
    {
      name: 'baikao-backend',
      script: 'python',
      args: '/app/backend/src/main.py',
      cwd: '/app/backend',
      instances: 'max',
      exec_mode: 'cluster',
      watch: false,
      max_memory_restart: '1G',
      env: {
        FLASK_ENV: 'production',
        PYTHONPATH: '/app/backend/src',
        PORT: 5000,
        HOST: '0.0.0.0'
      },
      env_production: {
        FLASK_ENV: 'production',
        PYTHONPATH: '/app/backend/src',
        PORT: 5000,
        HOST: '0.0.0.0'
      },
      env_development: {
        FLASK_ENV: 'development',
        PYTHONPATH: '/app/backend/src',
        PORT: 5000,
        HOST: '127.0.0.1'
      },
      log_file: '/app/logs/backend-combined.log',
      out_file: '/app/logs/backend-out.log',
      error_file: '/app/logs/backend-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      kill_timeout: 15000,
      wait_ready: true,
      listen_timeout: 15000,
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ],
  
  deploy: {
    production: {
      user: 'root',
      host: ['your-server.com'],
      ref: 'origin/main',
      repo: 'https://github.com/your-username/baikao-platform.git',
      path: '/var/www/baikao-platform',
      'pre-deploy-local': '',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env production',
      'pre-setup': '',
      ssh_options: 'StrictHostKeyChecking=no'
    },
    
    staging: {
      user: 'root',
      host: ['staging-server.com'],
      ref: 'origin/develop',
      repo: 'https://github.com/your-username/baikao-platform.git',
      path: '/var/www/baikao-platform-staging',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env staging'
    }
  }
};