import pickle

def test_color_pickle():
    from enaml.colors import Color
    rgba = 1, 2, 3, 4
    c = Color(*rgba)
    print(c.__reduce__())
    blob = pickle.dumps(c)
    c = pickle.loads(blob)
    assert (c.red, c.green, c.blue, c.alpha) == rgba
