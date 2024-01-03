import numpy

class Levenshtein(object):

    def __init__(self):
        super(Levenshtein, self).__init__()

    @staticmethod
    def editDistance(refer, hyper):
        """
        [step1] Levenshtein Distance 구현

        #비교하는 문자가 같은 경우 대각선 윗쪽의 값을 그대로
        #다를 경우 1)대각선, 2)좌측, 3)위 중 가장 작은 값에 +1 한 값

        :param refer: reference (비교 기준)
        :param hyper: STT result (비교할 텍스트)
        :return: Levenshtein Distance Matrix (len(r) * len(h))
        """
        # 1) (x+1)*(y+1) 0으로 초기화 된 매트릭스 생성
        len_refer = len(refer)
        len_hyper = len(hyper) 

        distance_matrix = [[0] * (len_hyper + 1) for _ in range(len_refer + 1)]

        # 2) 비용을 채워나가는 조건 구현
        for i in range(len_refer + 1):
            distance_matrix[i][0] = i

        for j in range(len_hyper + 1):
            distance_matrix[0][j] = j

        for i in range(1, len_refer + 1):
            for j in range(1, len_hyper + 1):
                if refer[i-1] == hyper[j-1]: # 비교하는 문자가 같으면 대각선 값을 그대로 가져온다.
                    distance_matrix[i][j] = distance_matrix[i-1][j-1]
                else:
                        distance_matrix[i][j] = min(distance_matrix[i-1][j],      # 삭제
                                        distance_matrix[i][j-1],                  # 삽입
                                        distance_matrix[i-1][j-1],) + 1           # 갱신
        # 3) 매트릭스 리턴
        return distance_matrix

    @staticmethod
    def getStepList(refer, hyper, distance_matrix):
        """
        [step2] TOT, MAT, INS, DEL, SUB 리스트 출력 함수
        #step2 : 매치, 삽입, 삭제, 대체 리스트 추적 함수 구현
        
        최종비용(x,y) 부터 시작하여 (0,0)까지 PATH -> 추적

        조건 1
        - 현재 비용 == 대각선 위 비용
        - 정답 음절 == 인식 음절
        - 매치(m)로 판단 -> 대각선 위로 이동

        조건 2
        - 현재 비용 == 위 비용  + 1
        - 삽입 에러(i)로 판단 -> 위로 이동
        
        조건 3
        - 현재 비용 == 대각선 위 비용 +1
        - 대체 에러(s)로 판단 -> 대각선 위로 이동
        
        조건 4
        - 모두 아닐 경우 삭제 에러(d)로 판단 -> 왼쪽으로 이동

        :param refer: Reference
        :param hyper: STT result
        :param distance_matrix: Levenshtein Distance Matrix
        :return:  Matched info list
        """

        # 구현
        x = len(refer)
        y = len(hyper)
        match_list = list()
    # 행렬의 끝에서 시작하여 최소 편집 경로 추적
        while x > 0 and y > 0:
            # 매치된 경우
            if refer[x - 1] == hyper[y - 1]:
                match_list.append("m")
                x -= 1
                y -= 1
            else:
                # 대체된 경우
                if distance_matrix[x][y] == distance_matrix[x-1][y-1] + 1:
                    match_list.append("s")
                    x -= 1
                    y -= 1
                # 삭제된 경우
                elif distance_matrix[x][y] == distance_matrix[x-1][y] + 1:
                    match_list.append("d")
                    x -= 1
                # 삽입된 경우
                else:
                    match_list.append("i")
                    y -= 1
        # 남은 차이 처리
        while x > 0:
            match_list.append("d")
            x -= 1
        while y > 0:
            match_list.append("i")
            y -= 1
        # matched info list 최종적으로 뒤집어서 리턴
        match_list = match_list[::-1]
        return match_list

def cer(info):
    """
    [step3] 음절 인식 결과 정보 리턴 함수

    :param r: Reference
    :param h: STT result
    :param d: Levenshtein Distance Matrix
    :return:  Matched info list
    """

    r_sent = info.get('ref')
    h_sent = info.get('hyp')

    distance = Levenshtein()  # YourClass는 Levenshtein 클래스의 인스턴스를 만든 것이라 가정합니다.

    matrix = distance.editDistance(r_sent, h_sent)  # step1

    match_list = distance.getStepList(r_sent, h_sent, matrix)  # step2

    # CER 계산
    num_total = len(matrix) - 1
    num_mat = match_list.count('m')
    num_sub = match_list.count('s')
    num_del = match_list.count('d')
    num_ins = match_list.count('i')
    cer_rate = ((num_total -(num_sub + num_del + num_ins)) / num_total) * 100

    # 리턴
    cer_info = {'cer': cer_rate, 'tot': num_total,
                'mat': num_mat, 'sub': num_sub,
                'del': num_del, 'ins': num_ins,
                'list': match_list}

    return cer_info


if __name__ == '__main__':

    refer1 = '안녕하세요 만나서 반갑습니다'  # 발성 내용
    hyper1 = '안녕하세용 만나스 반갑'  # 인식 결과

    refer2 = '사랑합니다'     # 발성 내용
    hyper2 = '서랑함다'      # 인식 결과

    refer3 = '나는너를좋아해'  # 발성 내용
    hyper3 = '너는나좋아하니'  # 인식 결과

    sentence_info1 = {'ref': refer1, 'hyp': hyper1}
    sentence_info2 = {'ref': refer2, 'hyp': hyper2}
    sentence_info3 = {'ref': refer3, 'hyp': hyper3}

    cer_info1 = cer(sentence_info1)
    cer_info2 = cer(sentence_info2)
    cer_info3 = cer(sentence_info3)

    print('refer : %s' % refer1)
    print('hyper : %s' % hyper1)
    print('match list : ', cer_info1.get('list'))
    cer_rate1 =  cer_info1.get('cer')
    print('cer : %f' % cer_rate1 if cer_rate1 > 0 else 0.0)

    print('tot : %d' % cer_info1.get('tot'))
    print('mat : %d' % cer_info1.get('mat'))
    print('sub : %d' % cer_info1.get('sub'))
    print('ins : %d' % cer_info1.get('ins'))
    print('del : %d' % cer_info1.get('del'))

    print('\n')

    print('refer : %s' % refer2)
    print('hyper : %s' % hyper2)
    print('match list : ', cer_info2.get('list'))
    cer_rate2 =  cer_info2.get('cer')
    print('cer : %f' % cer_rate2 if cer_rate2 > 0 else 0.0)
    
    print('tot : %d' % cer_info2.get('tot'))
    print('mat : %d' % cer_info2.get('mat'))
    print('sub : %d' % cer_info2.get('sub'))
    print('ins : %d' % cer_info2.get('ins'))
    print('del : %d' % cer_info2.get('del'))

    print('\n')

    print('refer : %s' % refer3)
    print('hyper : %s' % hyper3)
    print('match list : ', cer_info3.get('list'))
    cer_rate3 = cer_info3.get('cer')
    print('cer : %f' % cer_rate3 if cer_rate3 > 0 else 0.0)
    
    print('tot : %d' % cer_info3.get('tot'))
    print('mat : %d' % cer_info3.get('mat'))
    print('sub : %d' % cer_info3.get('sub'))
    print('ins : %d' % cer_info3.get('ins'))
    print('del : %d' % cer_info3.get('del'))