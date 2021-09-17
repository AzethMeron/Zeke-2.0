
def Parser():
    return dict()

def Add(parser, key, func):
    if key in parser:
        raise KeyError(f'{key} already present in parser')
    parser[key] = func

def Parse(parser, ctx, args):
    if len(args) < 1:
        raise ValueError("Not enough arguments")
    key = args.pop(0)
    if key not in parser:
        raise KeyError(f'{key} isn\'t a command')
    parser[key](ctx,args)