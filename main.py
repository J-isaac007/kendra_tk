"""
main.py — Kendra Pet Care Manager (Tkinter version)
Run with: python main.py
"""
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.app_controller import AppController


def main():
    controller = AppController()
    controller.run()


if __name__ == "__main__":
    main()