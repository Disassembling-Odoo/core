from psycopg2 import errorcodes, errors


PG_CONCURRENCY_ERRORS_TO_RETRY = (errorcodes.LOCK_NOT_AVAILABLE, errorcodes.SERIALIZATION_FAILURE, errorcodes.DEADLOCK_DETECTED)
PG_CONCURRENCY_EXCEPTIONS_TO_RETRY = (errors.LockNotAvailable, errors.SerializationFailure, errors.DeadlockDetected)
MAX_TRIES_ON_CONCURRENCY_FAILURE = 5


# Odoo module meta info file
# manifest file names
MANIFEST_NAMES = ('__manifest__.py', '__openerp__.py')
# readme file names
README = ['README.rst', 'README.md', 'README.txt']