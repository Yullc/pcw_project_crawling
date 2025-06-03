import pandas as pd
from sqlalchemy import create_engine

# 1. 엑셀 파일 불러오기
df = pd.read_excel('전국_축구장_결과.xlsx')

# 2. MySQL 연결 정보 설정
username = 'root'
password = ''
host = 'localhost'
port = '3307'
database = 'pcw_project'

# 3. SQLAlchemy 엔진 생성
engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}')

# 4. 데이터 삽입
df.to_sql(name='soccer_stadium', con=engine, if_exists='append', index=False)

print("✅ 데이터 삽입 완료!")
