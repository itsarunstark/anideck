import pyglet

# Create a resizable window
window = pyglet.window.Window(width=800, height=600, resizable=True)

# Load a font and create a label
label = pyglet.text.Label(
    'Hello, Pyglet!',
    font_name='Arial',
    font_size=36,
    x=window.width // 2,  # Start at center
    y=window.height // 2,  # Start at center
    anchor_x='center',
    anchor_y='center'
)

rect = pyglet.shapes.Rectangle(
    0,0, width=window.width, height=window.height, color=(255, 0, 0, 255)
)

@window.event
def on_draw():
    window.clear()
    label.draw()
    rect.draw()

@window.event
def on_resize(width, height):
    # Update the label's position to stay centered
    label.x = width // 2
    label.y = height // 2
    rect.width = width//2
    rect.height = height//2

# Run the application
pyglet.app.run()
