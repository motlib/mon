from monsrv import app, args, cfg

app.run(
    host=args.interface,
    port=args.port,
    debug=args.debug)
