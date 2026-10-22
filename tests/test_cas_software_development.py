"""Recognition boundaries and balanced software accounting templates."""
from dataclasses import replace
import unittest

from src import cas_software_development as software
from src.cas_software_development import SoftwareRecognition


class SoftwareDevelopmentTests(unittest.TestCase):
    def setUp(self):
        self.rd = SoftwareRecognition(
            'internal_rd', 'development', True, True, True,
            True, True, True, True, True,
        )

    def assertEntry(self, entry, expected):
        self.assertEqual([(x.account, x.debit, x.credit) for x in entry.lines], expected)
        self.assertAlmostEqual(sum(x.debit for x in entry.lines), sum(x.credit for x in entry.lines))

    def test_development_all_conditions(self):
        self.assertEqual(software.software_cost_treatment(self.rd), 'capitalize')

    def test_each_missing_condition_expenses(self):
        for field in list(vars(self.rd))[2:]:
            with self.subTest(field=field):
                self.assertEqual(software.software_cost_treatment(replace(self.rd, **{field: False})), 'expense')

    def test_research_and_indistinguishable_expense(self):
        for stage in ('research', 'indistinguishable'):
            self.assertEqual(software.software_cost_treatment(replace(self.rd, stage=stage)), 'expense')

    def test_purchase_does_not_require_rd_tests(self):
        facts = SoftwareRecognition('purchased_asset', controlled=True, probable_benefits=True, reliable_measurement=True)
        self.assertEqual(software.software_cost_treatment(facts), 'capitalize')
        self.assertEqual(software.client_software_cost_entry(facts, 100).lines[0].account, '无形资产—软件（待达到预定用途）')
        self.assertEqual(software.client_software_ready_entry(facts, 100, ready_for_use=True).lines[1].account, '无形资产—软件（待达到预定用途）')

    def test_service_and_unknown_evidence_expense(self):
        self.assertEqual(software.software_cost_treatment(replace(self.rd, nature='service')), 'expense')
        self.assertEqual(software.software_cost_treatment(SoftwareRecognition('internal_rd')), 'expense')

    def test_client_capitalization_and_deductible_vat(self):
        self.assertEntry(software.client_software_cost_entry(self.rd, 100, vat_amount=6, deductible_vat=True), [
            ('研发支出—资本化支出', 100, 0), ('应交税费—应交增值税（进项税额）', 6, 0), ('应付账款', 0, 106)])

    def test_non_deductible_vat_in_cost(self):
        for facts, account in ((self.rd, '研发支出—资本化支出'),
                               (replace(self.rd, stage='research'), '管理费用—研发费用'),
                               (SoftwareRecognition('service'), '管理费用—软件服务费')):
            self.assertEntry(software.client_software_cost_entry(facts, 100, vat_amount=6), [(account, 106, 0), ('应付账款', 0, 106)])

    def test_ready_transfer(self):
        self.assertEntry(software.client_software_ready_entry(self.rd, 106, ready_for_use=True), [
            ('无形资产—软件', 106, 0), ('研发支出—资本化支出', 0, 106)])
        for facts, ready in ((self.rd, False), (replace(self.rd, stage='research'), True)):
            with self.assertRaises(ValueError):
                software.client_software_ready_entry(facts, 106, ready_for_use=ready)

    def test_cash_entries(self):
        for party, advance, debit, credit in (
            ('client', True, '预付账款', '银行存款'), ('client', False, '应付账款', '银行存款'),
            ('contractor', True, '银行存款', '合同负债'), ('contractor', False, '银行存款', '应收账款')):
            self.assertEntry(software.software_cash_entry(party, 106, advance=advance), [(debit, 106, 0), (credit, 0, 106)])

    def test_contractor_revenue_and_vat(self):
        for unconditional, account in ((True, '应收账款'), (False, '合同资产')):
            self.assertEntry(software.contractor_software_revenue_entry(100, recognition_confirmed=True, unconditional_receivable=unconditional, vat_amount=6), [
                (account, 106, 0), ('主营业务收入—软件开发', 0, 100), ('应交税费—应交增值税（销项税额）', 0, 6)])
        with self.assertRaises(ValueError):
            software.contractor_software_revenue_entry(100, recognition_confirmed=False)

    def test_contractor_costs_and_release(self):
        for future, account in ((True, '合同履约成本'), (False, '主营业务成本')):
            self.assertEntry(software.contractor_software_cost_entry(60, future_performance_asset=future), [(account, 60, 0), ('应付账款', 0, 60)])
        self.assertEntry(software.contractor_software_cost_release_entry(60), [('主营业务成本', 60, 0), ('合同履约成本', 0, 60)])

    def test_invalid_money_every_entry(self):
        calls = [lambda n: software.client_software_cost_entry(self.rd, n),
                 lambda n: software.client_software_ready_entry(self.rd, n, ready_for_use=True),
                 lambda n: software.software_cash_entry('client', n),
                 lambda n: software.contractor_software_revenue_entry(n, recognition_confirmed=True),
                 software.contractor_software_cost_entry, software.contractor_software_cost_release_entry]
        for call in calls:
            for value in (0, -1, float('nan'), float('inf'), -float('inf'), True, '100', None):
                with self.subTest(call=call, value=value), self.assertRaises(ValueError):
                    call(value)

    def test_invalid_tax(self):
        for value in (-1, float('nan'), float('inf'), True, None):
            with self.assertRaises(ValueError):
                software.client_software_cost_entry(self.rd, 100, vat_amount=value)
            with self.assertRaises(ValueError):
                software.contractor_software_revenue_entry(100, recognition_confirmed=True, vat_amount=value)

    def test_invalid_facts_flags_and_enums(self):
        for kwargs in ({'nature': 'bad'}, {'stage': 'bad'}, {'controlled': 1}):
            with self.assertRaises(ValueError):
                replace(self.rd, **kwargs)
        calls = [lambda: software.software_cost_treatment(None),
                 lambda: software.software_cash_entry('bad', 10),
                 lambda: software.software_cash_entry('client', 10, advance=1),
                 lambda: software.client_software_cost_entry(self.rd, 10, deductible_vat=1),
                 lambda: software.client_software_ready_entry(self.rd, 10, ready_for_use=1),
                 lambda: software.contractor_software_revenue_entry(10, recognition_confirmed=1),
                 lambda: software.contractor_software_revenue_entry(10, recognition_confirmed=True, unconditional_receivable=1),
                 lambda: software.contractor_software_cost_entry(10, future_performance_asset=1)]
        for call in calls:
            with self.assertRaises(ValueError):
                call()

    def test_overflow_rejected(self):
        with self.assertRaises(ValueError):
            software.client_software_cost_entry(self.rd, 1e308, vat_amount=1e308)
        with self.assertRaises(ValueError):
            software.contractor_software_revenue_entry(1e308, recognition_confirmed=True, vat_amount=1e308)

    def test_root_exports(self):
        import src
        self.assertIs(src.SoftwareRecognition, SoftwareRecognition)
        self.assertIs(src.client_software_cost_entry, software.client_software_cost_entry)
