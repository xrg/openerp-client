
def logged(showtime):
    def log(f, res, *args, **kwargs):
        vector = ['Call -> function: %s' % f]
        for i, arg in enumerate(args):
            vector.append( '  arg %02d: %r' % ( i, arg ) )
        for key, value in kwargs.items():
            vector.append( '  kwarg %10s: %r' % ( key, value ) )
        vector.append( '  result: %r' % res )
        print "\n".join(vector)

    def outerwrapper(f):
        def wrapper(*args, **kwargs):
            if showtime:
                import time
                now = time.time()
            res = None
            try:
                res = f(*args, **kwargs)
                return res
            finally:
                log(f, res, *args, **kwargs)
                if showtime:
                    print "  time delta: %s" % (time.time() - now)
        return wrapper
    return outerwrapper

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
