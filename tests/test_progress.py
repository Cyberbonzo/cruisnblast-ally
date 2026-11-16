"""Synthetic save fixtures only; no game data is distributed."""
from pathlib import Path
import struct,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from progress import Progress,valid

def profile():
    data=bytearray(324);data[8:17]=b'24682468\0'
    h=2166136261
    for b in data:h=((h^b)*16777619)&0xffffffff
    return struct.pack('<II',0x31504243,h)+data

class Backups(unittest.TestCase):
    def test_recovery_rotation_and_current_state(self):
        with tempfile.TemporaryDirectory() as root:
            p=Progress(root);p.state.mkdir(parents=True)
            table=struct.pack('<IH',972008,10)+bytes(972002)
            originals={'player_tbl':table,'ally-profile.bin':profile()}
            for name,data in originals.items():(p.state/name).write_bytes(data)
            p.backup()
            for name in originals:(p.state/name).write_bytes(b'broken')
            p.restore()
            for name,data in originals.items():self.assertEqual((p.state/name).read_bytes(),data)
            preference=p.state/'ally-infinite-blast.cfg'
            preference.write_bytes(b'0\n');p.backup()
            preference.write_bytes(b'1\n');p.restore()
            self.assertEqual(preference.read_bytes(),b'1\n')
            for i in range(12):preference.write_text(str(i));p.backup()
            self.assertEqual(len(list(p.backups.glob('*.zip'))),8)

    def test_integrity(self):
        good=profile();self.assertTrue(valid('ally-profile.bin',good))
        damaged=bytearray(good);damaged[50]^=1
        self.assertFalse(valid('ally-profile.bin',damaged))
        self.assertFalse(valid('ally-profile.bin',good[:-1]))
        self.assertFalse(valid('player_tbl',bytes(972008)))

if __name__=='__main__':unittest.main()
