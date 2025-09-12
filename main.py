import csg
import ray_marching

import tkinter as tk

WIDTH = 400
HEIGHT = 600 

window = tk.Tk()
window.title("Adams CSG")

canvas = tk.Canvas(window,width=WIDTH,height=HEIGHT,bg="white")
canvas.pack()

