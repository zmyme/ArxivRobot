def func(a, b, c, time=0, work=1):
	print('a:{0} b:{1} c:{2}'.format(a, b, c))
	print('time:{0} work:{1}'.format(time, work))

def funcwrap(func, kargs, kkargs):
	func(*kargs, **kkargs)


kargs = [1, 2, 3]
kkargs = {
	"time":1234,
	"work":1232
}

funcwrap(func, kargs, kkargs)