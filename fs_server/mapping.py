from filetree import File


class FileSystem:
    def __init__(self, url_root: str, fs_root: str):
        self.url_root = url_root
        self.fs_root = fs_root

    def url2fs(self, url_path: str):
        return url_path.replace(self.url_root, self.fs_root)

    def file(self, url_path: str):
        if not url_path.startswith(self.url_root):
            return None
        return File(self.url2fs(url_path))


def test():
    fs = FileSystem('/public', './dist')
    assert fs.file('/public/css/style.css').relpath == 'dist/css/style.css'
