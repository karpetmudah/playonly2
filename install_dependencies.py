#!/usr/bin/env python3
"""
Installation script for OpenHands SaaS dependencies
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors"""
    print(f'🔄 {description}...')
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f'✅ {description} completed successfully')
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f'❌ {description} failed:')
        print(f'Error: {e.stderr}')
        return None


def install_dependencies():
    """Install required dependencies for SaaS mode"""
    print('🚀 Installing OpenHands SaaS dependencies...')

    # Install Python dependencies
    commands = [
        ('poetry install', 'Installing Python dependencies'),
        (
            'poetry add motor pymongo bcrypt email-validator',
            'Installing SaaS-specific dependencies',
        ),
    ]

    for command, description in commands:
        result = run_command(command, description)
        if result is None:
            print(f'❌ Failed to execute: {command}')
            return False

    return True


def setup_environment():
    """Setup environment configuration"""
    print('🔧 Setting up environment configuration...')

    # Check if .env exists
    if not os.path.exists('.env'):
        if os.path.exists('.env.saas.example'):
            print('📋 Copying .env.saas.example to .env...')
            run_command('cp .env.saas.example .env', 'Copying environment template')
            print('⚠️  Please edit .env file with your MongoDB URL and JWT secret!')
        else:
            print('⚠️  .env.saas.example not found. Please create .env manually.')
    else:
        print('✅ .env file already exists')


def main():
    """Main installation function"""
    print('🎯 OpenHands SaaS Installation Script')
    print('=' * 50)

    # Check if we're in the right directory
    if not os.path.exists('pyproject.toml'):
        print(
            '❌ pyproject.toml not found. Please run this script from the OpenHands root directory.'
        )
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print('❌ Dependency installation failed')
        sys.exit(1)

    # Setup environment
    setup_environment()

    print('\n🎉 Installation completed!')
    print('\n📝 Next steps:')
    print('1. Edit .env file with your MongoDB URL and JWT secret')
    print('2. Start MongoDB (if running locally)')
    print('3. Run: make build && make run')
    print('\n🔗 For MongoDB Atlas setup, visit: https://cloud.mongodb.com/')


if __name__ == '__main__':
    main()
