import pyglet
from pyglet.window import key

# Create a window
window = pyglet.window.Window(fullscreen=False)

@window.event
def on_key_press(symbol, modifiers):
    # Toggle fullscreen on F11 key press
    if symbol == key.F11:
        window.set_fullscreen(not window.fullscreen)

# Run the Pyglet application loop
pyglet.app.run()