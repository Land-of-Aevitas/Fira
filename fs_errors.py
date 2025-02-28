'''Errors for the FiraScript interpreter.'''

class FSError(Exception):
    '''Parent for all FiraScript errors.'''
class FSSyntaxError(FSError):
    '''Raised when the syntax of the FiraScript is incorrect.'''
class FSRecursionError(FSError):
    '''Raised when the recursion depth is too high.'''
class FSOSError(FSError):
    '''Raised when there is an OS/file error.'''
class FSNotDefinedError(FSError):
    '''Raised when attempting to transalte an undefined word'''
