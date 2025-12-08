
class AppContext:
    def __init__(self, config_path=None, verbose=0, quiet=False, dry_run=False):
        self.config_path = config_path
        self.verbose = verbose
        self.quiet = quiet
        self.dry_run = dry_run
        self.config = None