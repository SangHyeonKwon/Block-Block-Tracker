"""pytest 설정."""

import sys
import os

# tracker-bot 디렉토리를 sys.path에 추가하여 모듈 임포트 가능하게 함
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
