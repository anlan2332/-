// PM2 Local Development Configuration for BaiKaoTong AI Writing Platform

module.exports = {
  apps: [
    {
      name: 'baikao-frontend-local',
      script: 'npm',
      args: 'run dev',
      cwd: './frontend',
      instances: 1,
      exec_mode: 'fork',
      watch: ['src/**/*'],
      ignore_watch: ['node_modules', 'build', 'logs'],
      watch_options: {
        followSymlinks: false
      },
      max_memory_restart: '300M',
      env: {
        NODE_ENV: 'development',
        PORT: 3000,
        HOST: '127.0.0.1',
        BROWSER: 'none',
        GENERATE_SOURCEMAP: 'false'
      },
      log_file: './logs/frontend-dev-combined.log',
      out_file: './logs/frontend-dev-out.log',
      error_file: './logs/frontend-dev-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      kill_timeout: 5000
    },
    {
      name: 'baikao-backend-local',
      script: 'python',
      args: 'backend/src/main.py',
      cwd: '.',
      instances: 1,
      exec_mode: 'fork',
      watch: ['backend/src/**/*.py'],
      ignore_watch: ['backend/__pycache__', 'logs', 'uploads'],
      max_memory_restart: '500M',
      env: {
        FLASK_ENV: 'development',
        FLASK_DEBUG: '1',
        PYTHONPATH: './backend/src',
        PORT: 5000,
        HOST: '127.0.0.1',
        DB_TYPE: 'sqlite',
        DB_PATH: './data/local.db'
      },
      log_file: './logs/backend-dev-combined.log',
      out_file: './logs/backend-dev-out.log',
      error_file: './logs/backend-dev-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      kill_timeout: 10000,
      restart_delay: 2000
    }
  ]
};