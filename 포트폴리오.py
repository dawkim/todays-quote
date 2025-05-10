import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class PortfolioTracker:
    def __init__(self):
        # 국내 ISA 계좌 포트폴리오
        self.isa_portfolio = {
            "현금": 0,
            "주식": {},
            "ETF": {}
        }
        
        # 미국 직접 투자 포트폴리오
        self.us_portfolio = {
            "현금": 0,
            "주식": {}
        }
        
        # 거래 기록
        self.transactions = []
        
        # 환율 정보 (KRW/USD)
        self.exchange_rate = 1300  # 기본값, 업데이트 가능
        
    def set_exchange_rate(self, rate):
        """환율 설정"""
        self.exchange_rate = rate
        print(f"환율이 {rate}원/달러로 설정되었습니다.")
    
    def deposit_cash(self, account_type, amount):
        """현금 입금"""
        if account_type.lower() == "isa":
            self.isa_portfolio["현금"] += amount
            account = "ISA"
        elif account_type.lower() == "us":
            self.us_portfolio["현금"] += amount
            account = "US"
        else:
            print("잘못된 계좌 유형입니다. 'ISA' 또는 'US'를 입력하세요.")
            return
        
        self.transactions.append({
            "날짜": datetime.now().strftime("%Y-%m-%d"),
            "유형": "입금",
            "계좌": account,
            "금액": amount,
            "설명": f"{account} 계좌에 {amount:,}원 입금"
        })
        
        print(f"{account} 계좌에 {amount:,}원이 입금되었습니다.")
    
    def buy_stock(self, account_type, ticker, name, price, quantity, currency="KRW"):
        """주식 매수"""
        total_cost = price * quantity
        
        if account_type.lower() == "isa":
            # ISA 계좌에서 매수
            if currency != "KRW":
                # 외화 -> 원화 변환
                total_cost_krw = total_cost * self.exchange_rate
            else:
                total_cost_krw = total_cost
                
            if self.isa_portfolio["현금"] < total_cost_krw:
                print("ISA 계좌에 현금이 부족합니다.")
                return
            
            # 주식인지 ETF인지 확인 (간단한 방법: 이름에 'ETF'가 포함되어 있으면 ETF로 간주)
            is_etf = "ETF" in name.upper()
            
            # 매수 처리
            self.isa_portfolio["현금"] -= total_cost_krw
            
            if is_etf:
                if ticker in self.isa_portfolio["ETF"]:
                    # 기존 보유 ETF에 추가
                    old_quantity = self.isa_portfolio["ETF"][ticker]["수량"]
                    old_price = self.isa_portfolio["ETF"][ticker]["매수가"]
                    
                    # 평균 매수가 재계산
                    new_quantity = old_quantity + quantity
                    new_price = (old_price * old_quantity + price * quantity) / new_quantity
                    
                    self.isa_portfolio["ETF"][ticker] = {
                        "이름": name,
                        "수량": new_quantity,
                        "매수가": new_price,
                        "현재가": price,
                        "통화": currency
                    }
                else:
                    # 새 ETF 추가
                    self.isa_portfolio["ETF"][ticker] = {
                        "이름": name,
                        "수량": quantity,
                        "매수가": price,
                        "현재가": price,
                        "통화": currency
                    }
                
                asset_type = "ETF"
            else:
                if ticker in self.isa_portfolio["주식"]:
                    # 기존 보유 주식에 추가
                    old_quantity = self.isa_portfolio["주식"][ticker]["수량"]
                    old_price = self.isa_portfolio["주식"][ticker]["매수가"]
                    
                    # 평균 매수가 재계산
                    new_quantity = old_quantity + quantity
                    new_price = (old_price * old_quantity + price * quantity) / new_quantity
                    
                    self.isa_portfolio["주식"][ticker] = {
                        "이름": name,
                        "수량": new_quantity,
                        "매수가": new_price,
                        "현재가": price,
                        "통화": currency
                    }
                else:
                    # 새 주식 추가
                    self.isa_portfolio["주식"][ticker] = {
                        "이름": name,
                        "수량": quantity,
                        "매수가": price,
                        "현재가": price,
                        "통화": currency
                    }
                
                asset_type = "주식"
            
            account = "ISA"
            
        elif account_type.lower() == "us":
            # 미국 주식 직접 투자 계좌에서 매수
            if currency != "USD":
                # 원화 -> 달러 변환
                total_cost_usd = total_cost / self.exchange_rate
            else:
                total_cost_usd = total_cost
            
            total_cost_krw = total_cost_usd * self.exchange_rate
            
            if self.us_portfolio["현금"] < total_cost_krw:
                print("미국 주식 계좌에 현금이 부족합니다.")
                return
            
            # 매수 처리
            self.us_portfolio["현금"] -= total_cost_krw
            
            if ticker in self.us_portfolio["주식"]:
                # 기존 보유 주식에 추가
                old_quantity = self.us_portfolio["주식"][ticker]["수량"]
                old_price = self.us_portfolio["주식"][ticker]["매수가"]
                
                # 평균 매수가 재계산
                new_quantity = old_quantity + quantity
                new_price = (old_price * old_quantity + price * quantity) / new_quantity
                
                self.us_portfolio["주식"][ticker] = {
                    "이름": name,
                    "수량": new_quantity,
                    "매수가": new_price,
                    "현재가": price,
                    "통화": "USD"  # 미국 주식은 USD로 고정
                }
            else:
                # 새 주식 추가
                self.us_portfolio["주식"][ticker] = {
                    "이름": name,
                    "수량": quantity,
                    "매수가": price,
                    "현재가": price,
                    "통화": "USD"  # 미국 주식은 USD로 고정
                }
            
            account = "US"
            asset_type = "주식"
        else:
            print("잘못된 계좌 유형입니다. 'ISA' 또는 'US'를 입력하세요.")
            return
        
        # 거래 기록 추가
        self.transactions.append({
            "날짜": datetime.now().strftime("%Y-%m-%d"),
            "유형": "매수",
            "계좌": account,
            "종목": ticker,
            "이름": name,
            "가격": price,
            "수량": quantity,
            "총액": total_cost_krw if currency == "KRW" or account_type.lower() == "us" else total_cost,
            "통화": "KRW" if currency == "KRW" or account_type.lower() == "us" else currency
        })
        
        print(f"{account} 계좌에서 {name}({ticker}) {quantity}주를 {price:,.2f}{currency}에 매수했습니다.")
        
    def sell_stock(self, account_type, ticker, price, quantity, tax_rate=0.22):
        """주식 매도"""
        if account_type.lower() == "isa":
            # ISA 계좌에서 매도
            is_etf = ticker in self.isa_portfolio["ETF"]
            
            if is_etf:
                if ticker not in self.isa_portfolio["ETF"]:
                    print(f"ISA 계좌에 {ticker} ETF가 없습니다.")
                    return
                
                if self.isa_portfolio["ETF"][ticker]["수량"] < quantity:
                    print(f"ISA 계좌에 충분한 {ticker} ETF가 없습니다.")
                    return
                
                # 매도 처리
                currency = self.isa_portfolio["ETF"][ticker]["통화"]
                name = self.isa_portfolio["ETF"][ticker]["이름"]
                buy_price = self.isa_portfolio["ETF"][ticker]["매수가"]
                
                # 수익 계산
                if currency == "KRW":
                    total_proceeds = price * quantity
                else:
                    # 외화 -> 원화 변환
                    total_proceeds = price * quantity * self.exchange_rate
                
                # ISA 계좌 내 비과세 혜택 가정 (실제로는 조건에 따라 다름)
                tax_amount = 0  # ISA 계좌는 비과세 가정
                
                # 현금 추가
                self.isa_portfolio["현금"] += total_proceeds - tax_amount
                
                # ETF 수량 업데이트
                if self.isa_portfolio["ETF"][ticker]["수량"] == quantity:
                    # 전량 매도
                    del self.isa_portfolio["ETF"][ticker]
                else:
                    # 일부 매도
                    self.isa_portfolio["ETF"][ticker]["수량"] -= quantity
                
                asset_type = "ETF"
            else:
                if ticker not in self.isa_portfolio["주식"]:
                    print(f"ISA 계좌에 {ticker} 주식이 없습니다.")
                    return
                
                if self.isa_portfolio["주식"][ticker]["수량"] < quantity:
                    print(f"ISA 계좌에 충분한 {ticker} 주식이 없습니다.")
                    return
                
                # 매도 처리
                currency = self.isa_portfolio["주식"][ticker]["통화"]
                name = self.isa_portfolio["주식"][ticker]["이름"]
                buy_price = self.isa_portfolio["주식"][ticker]["매수가"]
                
                # 수익 계산
                if currency == "KRW":
                    total_proceeds = price * quantity
                else:
                    # 외화 -> 원화 변환
                    total_proceeds = price * quantity * self.exchange_rate
                
                # ISA 계좌 내 비과세 혜택 가정 (실제로는 조건에 따라 다름)
                tax_amount = 0  # ISA 계좌는 비과세 가정
                
                # 현금 추가
                self.isa_portfolio["현금"] += total_proceeds - tax_amount
                
                # 주식 수량 업데이트
                if self.isa_portfolio["주식"][ticker]["수량"] == quantity:
                    # 전량 매도
                    del self.isa_portfolio["주식"][ticker]
                else:
                    # 일부 매도
                    self.isa_portfolio["주식"][ticker]["수량"] -= quantity
                
                asset_type = "주식"
            
            account = "ISA"
            
        elif account_type.lower() == "us":
            # 미국 주식 계좌에서 매도
            if ticker not in self.us_portfolio["주식"]:
                print(f"미국 주식 계좌에 {ticker} 주식이 없습니다.")
                return
            
            if self.us_portfolio["주식"][ticker]["수량"] < quantity:
                print(f"미국 주식 계좌에 충분한 {ticker} 주식이 없습니다.")
                return
            
            # 매도 처리
            name = self.us_portfolio["주식"][ticker]["이름"]
            buy_price = self.us_portfolio["주식"][ticker]["매수가"]
            
            # 수익 계산 (달러 기준)
            total_proceeds_usd = price * quantity
            total_proceeds_krw = total_proceeds_usd * self.exchange_rate
            
            # 세금 계산 (매도 이익에 대한 양도소득세)
            profit_usd = (price - buy_price) * quantity
            profit_krw = profit_usd * self.exchange_rate
            
            # 연간 250만원 초과분에만 세금 적용 (예시, 실제로는 연간 수익 합산 필요)
            # 이 예제에서는 단순화를 위해 모든 이익에 바로 세율 적용
            if profit_krw > 0:
                tax_amount_krw = profit_krw * tax_rate
            else:
                tax_amount_krw = 0
            
            # 현금 추가 (원화 기준)
            self.us_portfolio["현금"] += total_proceeds_krw - tax_amount_krw
            
            # 주식 수량 업데이트
            if self.us_portfolio["주식"][ticker]["수량"] == quantity:
                # 전량 매도
                del self.us_portfolio["주식"][ticker]
            else:
                # 일부 매도
                self.us_portfolio["주식"][ticker]["수량"] -= quantity
            
            account = "US"
            asset_type = "주식"
            currency = "USD"
        else:
            print("잘못된 계좌 유형입니다. 'ISA' 또는 'US'를 입력하세요.")
            return
        
        # 거래 기록 추가
        self.transactions.append({
            "날짜": datetime.now().strftime("%Y-%m-%d"),
            "유형": "매도",
            "계좌": account,
            "종목": ticker,
            "이름": name,
            "가격": price,
            "수량": quantity,
            "총액": total_proceeds_krw if account_type.lower() == "us" else (total_proceeds if currency == "KRW" else total_proceeds),
            "손익": profit_krw if account_type.lower() == "us" else ((price - buy_price) * quantity),
            "세금": tax_amount_krw if account_type.lower() == "us" and profit_krw > 0 else 0,
            "통화": "KRW" if currency == "KRW" or account_type.lower() == "us" else currency
        })
        
        profit_str = f", 수익: {profit_krw:,.2f}원" if account_type.lower() == "us" else f", 수익: {(price - buy_price) * quantity:,.2f}{currency}"
        tax_str = f", 세금: {tax_amount_krw:,.2f}원" if account_type.lower() == "us" and profit_krw > 0 else ""
        
        print(f"{account} 계좌에서 {name}({ticker}) {quantity}주를 {price:,.2f}{currency if account_type.lower() != 'us' else 'USD'}에 매도했습니다{profit_str}{tax_str}")
    
    def update_price(self, account_type, ticker, new_price):
        """현재가 업데이트"""
        if account_type.lower() == "isa":
            # ISA 계좌 종목 가격 업데이트
            if ticker in self.isa_portfolio["ETF"]:
                self.isa_portfolio["ETF"][ticker]["현재가"] = new_price
                name = self.isa_portfolio["ETF"][ticker]["이름"]
                asset_type = "ETF"
            elif ticker in self.isa_portfolio["주식"]:
                self.isa_portfolio["주식"][ticker]["현재가"] = new_price
                name = self.isa_portfolio["주식"][ticker]["이름"]
                asset_type = "주식"
            else:
                print(f"ISA 계좌에 {ticker} 종목이 없습니다.")
                return
            
            account = "ISA"
        elif account_type.lower() == "us":
            # 미국 주식 가격 업데이트
            if ticker in self.us_portfolio["주식"]:
                self.us_portfolio["주식"][ticker]["현재가"] = new_price
                name = self.us_portfolio["주식"][ticker]["이름"]
                asset_type = "주식"
            else:
                print(f"미국 주식 계좌에 {ticker} 종목이 없습니다.")
                return
            
            account = "US"
        else:
            print("잘못된 계좌 유형입니다. 'ISA' 또는 'US'를 입력하세요.")
            return
        
        print(f"{account} 계좌의 {name}({ticker}) 현재가를 {new_price:,.2f}로 업데이트했습니다.")
    
    def calculate_portfolio_value(self):
        """포트폴리오 총 가치 계산"""
        # ISA 계좌 가치 계산
        isa_value = self.isa_portfolio["현금"]
        
        for ticker, stock in self.isa_portfolio["주식"].items():
            if stock["통화"] == "KRW":
                isa_value += stock["현재가"] * stock["수량"]
            else:
                # 외화 -> 원화 변환
                isa_value += stock["현재가"] * stock["수량"] * self.exchange_rate
        
        for ticker, etf in self.isa_portfolio["ETF"].items():
            if etf["통화"] == "KRW":
                isa_value += etf["현재가"] * etf["수량"]
            else:
                # 외화 -> 원화 변환
                isa_value += etf["현재가"] * etf["수량"] * self.exchange_rate
        
        # 미국 직접 투자 계좌 가치 계산
        us_value = self.us_portfolio["현금"]
        
        for ticker, stock in self.us_portfolio["주식"].items():
            # 달러 -> 원화 변환
            us_value += stock["현재가"] * stock["수량"] * self.exchange_rate
        
        # 전체 포트폴리오 가치
        total_value = isa_value + us_value
        
        return {
            "ISA 계좌 가치": isa_value,
            "미국 주식 계좌 가치": us_value,
            "전체 포트폴리오 가치": total_value
        }
    
    def calculate_returns(self):
        """수익률 계산"""
        # ISA 계좌 수익률 계산
        isa_invested = 0
        isa_current = self.isa_portfolio["현금"]
        
        for ticker, stock in self.isa_portfolio["주식"].items():
            cost_basis = stock["매수가"] * stock["수량"]
            current_value = stock["현재가"] * stock["수량"]
            
            if stock["통화"] != "KRW":
                # 외화 -> 원화 변환
                cost_basis *= self.exchange_rate
                current_value *= self.exchange_rate
            
            isa_invested += cost_basis
            isa_current += current_value
        
        for ticker, etf in self.isa_portfolio["ETF"].items():
            cost_basis = etf["매수가"] * etf["수량"]
            current_value = etf["현재가"] * etf["수량"]
            
            if etf["통화"] != "KRW":
                # 외화 -> 원화 변환
                cost_basis *= self.exchange_rate
                current_value *= self.exchange_rate
            
            isa_invested += cost_basis
            isa_current += current_value
        
        # 거래 기록에서 입금 내역 확인하여 실제 투자금 계산
        total_isa_deposits = 0
        for transaction in self.transactions:
            if transaction["유형"] == "입금" and transaction["계좌"] == "ISA":
                total_isa_deposits += transaction["금액"]
        
        isa_return_vs_cost = (isa_current / isa_invested - 1) * 100 if isa_invested > 0 else 0
        isa_return_vs_deposit = (isa_current / total_isa_deposits - 1) * 100 if total_isa_deposits > 0 else 0
        
        # 미국 직접 투자 계좌 수익률 계산
        us_invested = 0
        us_current = self.us_portfolio["현금"]
        
        for ticker, stock in self.us_portfolio["주식"].items():
            cost_basis = stock["매수가"] * stock["수량"] * self.exchange_rate
            current_value = stock["현재가"] * stock["수량"] * self.exchange_rate
            
            us_invested += cost_basis
            us_current += current_value
        
        # 거래 기록에서 입금 내역 확인하여 실제 투자금 계산
        total_us_deposits = 0
        for transaction in self.transactions:
            if transaction["유형"] == "입금" and transaction["계좌"] == "US":
                total_us_deposits += transaction["금액"]
        
        us_return_vs_cost = (us_current / us_invested - 1) * 100 if us_invested > 0 else 0
        us_return_vs_deposit = (us_current / total_us_deposits - 1) * 100 if total_us_deposits > 0 else 0
        
        # 전체 포트폴리오 수익률
        total_invested = isa_invested + us_invested
        total_current = isa_current + us_current
        total_deposits = total_isa_deposits + total_us_deposits
        
        total_return_vs_cost = (total_current / total_invested - 1) * 100 if total_invested > 0 else 0
        total_return_vs_deposit = (total_current / total_deposits - 1) * 100 if total_deposits > 0 else 0
        
        return {
            "ISA 계좌": {
                "투자 금액": isa_invested,
                "현재 가치": isa_current,
                "입금 금액": total_isa_deposits,
                "매수가 기준 수익률": isa_return_vs_cost,
                "입금액 기준 수익률": isa_return_vs_deposit
            },
            "미국 주식 계좌": {
                "투자 금액": us_invested,
                "현재 가치": us_current,
                "입금 금액": total_us_deposits,
                "매수가 기준 수익률": us_return_vs_cost,
                "입금액 기준 수익률": us_return_vs_deposit
            },
            "전체 포트폴리오": {
                "투자 금액": total_invested,
                "현재 가치": total_current,
                "입금 금액": total_deposits,
                "매수가 기준 수익률": total_return_vs_cost,
                "입금액 기준 수익률": total_return_vs_deposit
            }
        }
    
    def get_portfolio_allocation(self):
        """포트폴리오 자산 배분 현황"""
        # 각 종목별 현재 가치 계산
        assets = []
        
        # ISA 계좌 주식
        for ticker, stock in self.isa_portfolio["주식"].items():
            if stock["통화"] == "KRW":
                value = stock["현재가"] * stock["수량"]
            else:
                value = stock["현재가"] * stock["수량"] * self.exchange_rate
            
            assets.append({
                "계좌": "ISA",
                "유형": "주식",
                "종목코드": ticker,
                "종목명": stock["이름"],
                "현재가치": value
            })
        
        # ISA 계좌 ETF
        for ticker, etf in self.isa_portfolio["ETF"].items():
            if etf["통화"] == "KRW":
                value = etf["현재가"] * etf["수량"]
            else:
                value = etf["현재가"] * etf["수량"] * self.exchange_rate
            
            assets.append({
                "계좌": "ISA",
                "유형": "ETF",
                "종목코드": ticker,
                "종목명": etf["이름"],
                "현재가치": value
            })
        
        # 미국 직접 투자 계좌 주식
        for ticker, stock in self.us_portfolio["주식"].items():
            value = stock["현재가"] * stock["수량"] * self.exchange_rate
            
            assets.append({
                "계좌": "US",
                "유형": "주식",
                "종목코드": ticker,
                "종목명": stock["이름"],
                "현재가치": value
            })
        
        # 현금 추가
        assets.append({
            "계좌": "ISA",
            "유형": "현금",
            "종목코드": "CASH",
            "종목명": "현금(원화)",
            "현재가치": self.isa_portfolio["현금"]
        })
        
        assets.append({
            "계좌": "US",
            "유형": "현금",
            "종목코드": "CASH",
            "종목명": "현금(원화)",
            "현재가치": self.us_portfolio["현금"]
        })
        
        # 전체 포트폴리오 가치 계산
        portfolio_value = sum(asset["현재가치"] for asset in assets)
        
        # 비중 계산
        for asset in assets:
            asset["비중"] = (asset["현재가치"] / portfolio_value * 100) if portfolio_value > 0 else 0
        
        return assets
    
    def visualize_portfolio(self):
        """포트폴리오 시각화"""
        allocation = self.get_portfolio_allocation()
        
        # 종목별 비중 시각화
        labels = [f"{asset['종목명']} ({asset['계좌']})" for asset in allocation]
        sizes = [asset["비중"] for asset in allocation]
        colors = plt.cm.tab20.colors
        
        # 비중이 1% 미만인 항목은 '기타'로 묶기
        threshold = 1.0
        small_indices = [i for i, size in enumerate(sizes) if size < threshold]
        
        if small_indices:
            other_size = sum(sizes[i] for i in small_indices)
            
            # 작은 항목 제거
            labels = [labels[i] for i in range(len(labels)) if i not in small_indices]
            sizes = [sizes[i] for i in range(len(sizes)) if i not in small_indices]
            
            # '기타' 항목 추가
            if other_size > 0:
                labels.append('기타 (1% 미만)')
                sizes.append(other_size)
        
        # 파이 차트 그리기
        plt.figure(figsize=(10, 8))
        plt.pie(sizes, labels=None, colors=colors[:len(sizes)], autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('포트폴리오 자산 배분 (비중)')
        plt.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        
        # 계좌별 비중 시각화
        account_values = {}
        for asset in allocation:
            account = asset["계좌"]
            if account not in account_values:
                account_values[account] = 0
            account_values[account] += asset["현재가치"]
        
        account_labels = list(account_values.keys())
        account_sizes = list(account_values.values())
        
        # 총 포트폴리오 가치
        total_value = sum(account_sizes)
        
        # 비중 계산
        account_percentages = [(value / total_value * 100) for value in account_sizes]
        
        plt.figure(figsize=(10, 6))
        plt.bar(account_labels, account_percentages, color=['#ff9999', '#66b3ff'])
        plt.title('계좌별 자산 비중')
        plt.ylabel('비중 (%)')
        plt.ylim(0, 100)
        
        for i, percentage in enumerate(account_percentages):
            plt.text(i, percentage + 1, f'{percentage:.1f}%', ha='center')
        
        # 자산 유형별 비중 시각화
        type_values = {}
        for asset in allocation:
            asset_type = asset["유형"]
            if asset_type not in type_values:
                type_values[asset_type] = 0
            type_values[asset_type] += asset["현재가치"]
        
        type_labels =