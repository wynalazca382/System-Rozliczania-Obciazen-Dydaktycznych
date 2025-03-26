from sqlalchemy import Column, Integer, String, Float, Date, CheckConstraint, func, Text, ForeignKey, Index, CLOB
from sqlalchemy.orm import relationship, foreign, registry
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
registry().configure()
class DidacticCycles(Base):
    __tablename__ = 'DZ_CYKLE_DYDAKTYCZNE'

    KOD = Column(String(20), primary_key=True, index=True)
    OPIS = Column(String(100), nullable=False)
    DATA_OD = Column(Date, nullable=False)
    DATA_DO = Column(Date, nullable=False)
    CZY_WYSWIETLAC = Column(String(1), nullable=False, default='N')
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    DATA_ZAKON = Column(Date, nullable=False)
    TCDYD_KOD = Column(String(20), nullable=False)
    STATUS_CYKLU = Column(String(1), nullable=False, default='A')
    DESCRIPTION = Column(String(100), nullable=False)
    ARCHIWIZACJA_ZALICZEN = Column(String(1), nullable=False, default='N')
    DATA_MOD_ARCH_ZAL = Column(Date, nullable=False, default=func.sysdate())
    ARCHIWIZACJA_ETAPOW = Column(String(1), nullable=False, default='N')
    DATA_MOD_ARCH_ETP = Column(Date, nullable=False, default=func.sysdate())
    KOLEJNOSC = Column(Integer, nullable=True, default=0)

    committee_functions_pensum_end = relationship(
        "CommitteeFunctionPensum",
        back_populates="cycle_end",
        foreign_keys="[CommitteeFunctionPensum.CDYD_KON]"
    )
    committee_functions_pensum_start = relationship(
        "CommitteeFunctionPensum",
        back_populates="cycle_start",
        foreign_keys="[CommitteeFunctionPensum.CDYD_POCZ]"
    )
    subject_cycles = relationship(
    "SubjectCycle",
    back_populates="cycle",
    foreign_keys="SubjectCycle.CDYD_KOD"
)
    external_pensum = relationship(
        "ExternalPensum",
        back_populates="cycle",
        foreign_keys="[ExternalPensum.CDYD_KOD]"
    )
    positions_pensum_end = relationship(
        "StanowiskaZatrPensum",
        back_populates="cycle_end",
        foreign_keys="[StanowiskaZatrPensum.CDYD_KON]"
    )
    positions_pensum_start = relationship(
        "StanowiskaZatrPensum",
        back_populates="cycle_start",
        foreign_keys="[StanowiskaZatrPensum.CDYD_POCZ]"
    )
    groups = relationship(
        "Group",
        back_populates="didactic_cycle",
    )

    __table_args__ = (
        CheckConstraint("regexp_instr(KOD, '\\||''|&|%') = 0", name='check_kod'),
        CheckConstraint("CZY_WYSWIETLAC IN ('N', 'T')", name='check_czy_wyswietlac'),
        CheckConstraint("STATUS_CYKLU IN ('A', 'Z')", name='check_status_cyklu'),
        CheckConstraint("ARCHIWIZACJA_ZALICZEN IN ('N', 'A', 'X')", name='check_archiwizacja_zaliczen'),
        CheckConstraint("ARCHIWIZACJA_ETAPOW IN ('N', 'A', 'X')", name='check_archiwizacja_etapow'),
        Index('CDYD_KOLEJNOSC_UK', 'KOLEJNOSC', unique=True),
        Index('CDYD_TCDYD_FK_I', 'TCDYD_KOD')
    )

    cycles_pensum = relationship(
            "DidacticCyclesPensum",
            back_populates="cycle",
            foreign_keys="[DidacticCyclesPensum.CDYD_KOD]"
        )

class PensumSettlement(Base):
    __tablename__ = 'DZ_ROZLICZENIA_PENSUM'

    KOD = Column(String(20), primary_key=True, index=True)
    OPIS = Column(String(100), nullable=False)
    JEDN_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=False)
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    STATUS = Column(String(1), nullable=False, default='P')

    cycles_pensum = relationship(
        "DidacticCyclesPensum",
        back_populates="pensum_settlement",
        foreign_keys="[DidacticCyclesPensum.RPENS_KOD]"
    )
    committee_members = relationship(
        "CommitteeMember",
        back_populates="pensum_settlement",
        foreign_keys="[CommitteeMember.RPENS_KOD]"
    )
    individual_rates = relationship(
        "IndividualRates",
        back_populates="pensum_settlement",
        foreign_keys="[IndividualRates.RPENS_KOD]"
    )
    thesis_supervisors = relationship(
        "ThesisSupervisors",
        back_populates="pensum_settlement",
        foreign_keys="[ThesisSupervisors.RPENS_KOD]"
    )
    employee_pensum = relationship(
        "EmployeePensum",
        back_populates="pensum_settlement",
        foreign_keys="[EmployeePensum.RPENS_KOD]"
    )
    conversion_rates = relationship(
        "ConversionRate",
        back_populates="pensum_settlement",
        foreign_keys="[ConversionRate.RPENS_KOD]"
    )
    reviewers = relationship(
        "Reviewer",
        back_populates="pensum_settlement",
        foreign_keys="[Reviewer.RPENS_KOD]"
    )
    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="pensum_settlements",
        foreign_keys=[JEDN_KOD]
    )
    external_pensum = relationship(
        "ExternalPensum",
        back_populates="pensum_settlement",
        foreign_keys="[ExternalPensum.RPENS_KOD]"
    )
    discounts = relationship(
        "Discount",
        back_populates="pensum_settlement",
        foreign_keys="[Discount.RPENS_KOD]"
    )

    __table_args__ = (
        Index('RPENS_PK', 'KOD', unique=True),
    )

class DidacticCyclesPensum(Base):
    __tablename__ = 'DZ_CYKLE_PENSUM'

    CDYD_KOD = Column(String(20), ForeignKey('DZ_CYKLE_DYDAKTYCZNE.KOD'), primary_key=True, index=True)
    RPENS_KOD = Column(String(20), ForeignKey('DZ_ROZLICZENIA_PENSUM.KOD'), primary_key=True, index=True)
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())

    cycle = relationship(
        "DidacticCycles",
        back_populates="cycles_pensum",
        foreign_keys=[CDYD_KOD]
    )
    pensum_settlement = relationship(
        "PensumSettlement",
        back_populates="cycles_pensum",
        foreign_keys=[RPENS_KOD]
    )

    __table_args__ = (
        Index('CPENS_PK', 'CDYD_KOD', 'RPENS_KOD', unique=True),
    )

class CommitteeMember(Base):
    __tablename__ = 'DZ_CZLONEK_KOMISJI'

    OS_ID = Column(Integer, ForeignKey('DZ_OSOBY.ID'), primary_key=True, index=True)
    KOMI_ID = Column(Integer, ForeignKey('DZ_KOMISJE.ID'), primary_key=True, index=True)
    FUNKK_ID = Column(Integer, ForeignKey('DZ_FUNKCJE_W_KOMISJI.ID'), nullable=False)
    DATA_POCZ = Column(Date, nullable=True)
    DATA_KON = Column(Date, nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    UWAGI = Column(String(500), nullable=True)
    LICZBA_GODZ_ZA_PRACE = Column(Float, nullable=True)
    LICZBA_GODZ_DO_PENSUM = Column(Float, nullable=True)
    RPENS_KOD = Column(String(20), ForeignKey('DZ_ROZLICZENIA_PENSUM.KOD'), nullable=False)
    PRZEL_KOD = Column(String(20), ForeignKey('DZ_PRZELICZNIKI.PRZEL_KOD'), nullable=True)
    LICZBA_GODZ_PRZEN = Column(Float, nullable=True)

    committee = relationship(
        "Committee",
        back_populates="committee_members",
        foreign_keys=[KOMI_ID]
    )
    function = relationship(
        "CommitteeFunction",
        back_populates="committee_members",
        foreign_keys=[FUNKK_ID]
    )
    conversion_rate = relationship(
        "ConversionRate",
        back_populates="committee_members",
        foreign_keys=[RPENS_KOD, PRZEL_KOD]
    )
    pensum_settlement = relationship(
        "PensumSettlement",
        back_populates="committee_members",
        foreign_keys=[RPENS_KOD]
    )
    person = relationship(
        "Person",
        back_populates="committee_members",
        foreign_keys=[OS_ID]
    )

    __table_args__ = (
        Index('CZLO_INNI_PK', 'OS_ID', 'KOMI_ID', unique=True),
        Index('CZLO_KOMI_FK_I', 'KOMI_ID'),
        Index('CZLO_KOMI_FUNKK_FK_I', 'FUNKK_ID'),
        Index('CZLO_KOMI_PRZEL_FK_I', 'RPENS_KOD', 'PRZEL_KOD'),
        Index('CZLO_KOMI_RPENS_FK_I', 'RPENS_KOD'),
        Index('DZ_CZLONEK_KO_OS_FK_I', 'OS_ID')
    )

class Person(Base):
    __tablename__ = 'DZ_OSOBY'

    ID = Column(Integer, primary_key=True, index=True)
    PESEL = Column(String(11), nullable=True, unique=True)
    IMIE = Column(String(40), nullable=False)
    IMIE2 = Column(String(40), nullable=True)
    NAZWISKO = Column(String(40), nullable=False)
    DATA_UR = Column(Date, nullable=True)
    MIASTO_UR = Column(String(60), nullable=True)
    IMIE_OJCA = Column(String(40), nullable=True)
    IMIE_MATKI = Column(String(40), nullable=True)
    NAZWISKO_PANIEN_MATKI = Column(String(40), nullable=True)
    NAZWISKO_RODOWE = Column(String(40), nullable=True)
    SZKOLA = Column(String(200), nullable=True)
    SR_NR_DOWODU = Column(String(20), nullable=True)
    NIP = Column(String(13), nullable=True, unique=True)
    WKU_KOD = Column(String(20), ForeignKey('DZ_WKU.KOD'), nullable=True)
    KAT_WOJSKOWA = Column(String(1), nullable=True)
    STOSUNEK_WOJSKOWY = Column(String(20), nullable=True)
    UWAGI = Column(String(2000), nullable=True)
    WWW = Column(String(200), nullable=True)
    EMAIL = Column(String(100), nullable=True)
    OB_KOD = Column(String(20), ForeignKey('DZ_OBYWATELSTWA.KOD'), nullable=True)
    NAR_KOD = Column(String(20), ForeignKey('DZ_OBYWATELSTWA.KOD'), nullable=True)
    JED_ORG_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    PLEC = Column(String(1), nullable=False)
    TYTUL_PRZED = Column(Integer, ForeignKey('DZ_TYTULY.ID'), nullable=True)
    TYTUL_PO = Column(Integer, ForeignKey('DZ_TYTULY.ID'), nullable=True)
    CZY_POLONIA = Column(String(1), nullable=True)
    ZAMIEJSCOWA = Column(String(1), nullable=True)
    GDZIE_SOCJALNE = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=True)
    US_ID = Column(Integer, ForeignKey('DZ_URZEDY_SKARBOWE.ID'), nullable=True)
    AKAD_CZY_REZERWA = Column(String(1), nullable=False)
    AKAD_WYKROCZENIA = Column(String(1000), nullable=True)
    AKAD_UWAGI = Column(String(1000), nullable=True)
    SZK_ID = Column(Integer, ForeignKey('DZ_SZKOLY.ID'), nullable=True)
    POZIOM_UPRAWNIEN = Column(String(1), nullable=False)
    TDOK_KOD = Column(String(6), ForeignKey('DZ_TYPY_DOKUMENTOW.KOD'), nullable=True)
    NR_KARTY_BIBL = Column(String(30), nullable=True)
    BK_EMAIL = Column(String(100), nullable=True)
    KRAJ_URODZENIA = Column(String(20), ForeignKey('DZ_OBYWATELSTWA.KOD'), nullable=True)
    DANE_ZEW_STATUS = Column(String(1), nullable=False)
    OSIAGNIECIA = Column(Text, nullable=True)
    OSIAGNIECIA_ANG = Column(Text, nullable=True)
    EPUAP_IDENTYFIKATOR = Column(String(64), nullable=True)
    EPUAP_SKRYTKA = Column(String(64), nullable=True)
    KRAJ_DOK_KOD = Column(String(20), ForeignKey('DZ_OBYWATELSTWA.KOD'), nullable=True)
    DATA_WAZNOSCI_DOWODU = Column(Date, nullable=True)
    KWALIFIKACJE_WOJSKOWE = Column(String(300), nullable=True)
    KRAJ_SZKOLY_SREDNIEJ_KOD = Column(String(20), ForeignKey('DZ_OBYWATELSTWA.KOD'), nullable=True)

    committee_members = relationship(
        "CommitteeMember",
        back_populates="person",
        foreign_keys="[CommitteeMember.OS_ID]"
    )
    thesis_supervisors = relationship(
        "ThesisSupervisors",
        back_populates="person",
        foreign_keys="[ThesisSupervisors.OS_ID]"
    )
    social_unit = relationship(
        "OrganizationalUnits",
        back_populates="persons_social",
        foreign_keys=[GDZIE_SOCJALNE]
    )
    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="persons",
        foreign_keys=[JED_ORG_KOD]
    )
    post_title = relationship(
        "Title",
        back_populates="persons_with_post_title",
        foreign_keys=[TYTUL_PO]
    )
    pre_title = relationship(
        "Title",
        back_populates="persons_with_pre_title",
        foreign_keys=[TYTUL_PRZED]
    )
    employees = relationship(
        "Employee",
        back_populates="person",
        foreign_keys="[Employee.OS_ID]"
    )
    authored_reviews = relationship(
        "Reviewer",
        back_populates="author",
        foreign_keys="[Reviewer.AUTOR_OS_ID]"
    )
    reviews = relationship(
        "Reviewer",
        back_populates="person",
        foreign_keys="[Reviewer.OS_ID]"
    )
    
    __table_args__ = (
        Index('NIP_UK', 'NIP', unique=True),
        Index('OS_DOK_UK', 'PESEL', 'NIP', unique=True),
        Index('OS_GDZIE_SOC_FK_I', 'GDZIE_SOCJALNE'),
        Index('OS_JED_ORG_FK_I', 'JED_ORG_KOD'),
        Index('OS_KRAJ_SZKOLY_SRED_FK_I', 'KRAJ_SZKOLY_SREDNIEJ_KOD'),
        Index('OS_KRAJ_UR_FK_I', 'KRAJ_URODZENIA'),
        Index('OS_NAR_FK_I', 'NAR_KOD'),
        Index('OS_NAZWISKO_IMIE_SEARCH'),
        Index('OS_OB_FK_I', 'OB_KOD'),
        Index('OS_PK', 'ID', unique=True),
        Index('OS_SZK_FK_I', 'SZK_ID'),
        Index('OS_TDOK_FK_I', 'TDOK_KOD'),
        Index('OS_TYT_PO_FK_I', 'TYTUL_PO'),
        Index('OS_TYT_PRZED_FK_I', 'TYTUL_PRZED'),
        Index('OS_US_FK_I', 'US_ID'),
        Index('OS_WKU_FK_I', 'WKU_KOD'),
        Index('PESEL_UK', 'PESEL', unique=True)
    )

class CommitteeFunction(Base):
    __tablename__ = 'DZ_FUNKCJE_W_KOMISJI'

    ID = Column(Integer, primary_key=True, index=True)
    NAZWA = Column(String(100), nullable=False)
    TYPK_KOD = Column(String(20), ForeignKey('DZ_TYPY_KOMISJI.KOD'), nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    PENSUM_UCZELNIANE = Column(Integer, nullable=True)
    NAZWA_ANG = Column(String(100), nullable=True)

    committee_members = relationship(
        "CommitteeMember",
        back_populates="function",
        foreign_keys="[CommitteeMember.FUNKK_ID]"
    )
    committee_functions_pensum = relationship(
        "CommitteeFunctionPensum",
        back_populates="function",
        foreign_keys="[CommitteeFunctionPensum.FUNKK_ID]"
    )
    committee_type = relationship(
        "CommitteeType",
        back_populates="committee_functions",
        foreign_keys=[TYPK_KOD]
    )

    __table_args__ = (
        Index('FUNKK_PK', 'ID', unique=True),
        Index('FUNKK_TYPK_FK_I', 'TYPK_KOD'),
        Index('FUNKK_TYPK_KOD_NAZWA_UK', 'NAZWA', 'TYPK_KOD', unique=True)
    )

class CommitteeFunctionPensum(Base):
    __tablename__ = 'DZ_FUNKCJE_W_KOMISJI_PENSUM'

    ID = Column(Integer, primary_key=True, index=True)
    FUNKK_ID = Column(Integer, ForeignKey('DZ_FUNKCJE_W_KOMISJI.ID'), nullable=False)
    CDYD_POCZ = Column(String(20), ForeignKey('DZ_CYKLE_DYDAKTYCZNE.KOD'), nullable=False)
    PENSUM = Column(Integer, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    JED_ORG_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=False)
    CDYD_KON = Column(String(20), ForeignKey('DZ_CYKLE_DYDAKTYCZNE.KOD'), nullable=False)

    cycle_end = relationship(
        "DidacticCycles",
        back_populates="committee_functions_pensum_end",
        foreign_keys=[CDYD_KON]
    )
    cycle_start = relationship(
        "DidacticCycles",
        back_populates="committee_functions_pensum_start",
        foreign_keys=[CDYD_POCZ]
    )
    function = relationship(
        "CommitteeFunction",
        back_populates="committee_functions_pensum",
        foreign_keys=[FUNKK_ID]
    )
    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="committee_functions_pensum",
        foreign_keys=[JED_ORG_KOD]
    )
    
class DidacticCycleClasses(Base):
    __tablename__ = 'DZ_ZAJECIA_CYKLI'

    ID = Column(Integer, primary_key=True, index=True)
    PRZ_KOD = Column(String(20), ForeignKey('DZ_PRZEDMIOTY.KOD'), nullable=False)
    CDYD_KOD = Column(String(20), ForeignKey('DZ_CYKLE_DYDAKTYCZNE.KOD'), nullable=False)
    TZAJ_KOD = Column(String(20), ForeignKey('DZ_TYPY_ZAJEC.KOD'), nullable=False)
    LICZBA_GODZ = Column(Float, nullable=True)
    LIMIT_MIEJSC = Column(Integer, nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    WAGA_PENSUM = Column(Float, nullable=True)
    TPRO_KOD = Column(String(20), ForeignKey('DZ_TYPY_PROTOKOLOW.KOD'), nullable=True)
    EFEKTY_UCZENIA = Column(CLOB, nullable=True)
    EFEKTY_UCZENIA_ANG = Column(CLOB, nullable=True)
    KRYTERIA_OCENIANIA = Column(CLOB, nullable=True)
    KRYTERIA_OCENIANIA_ANG = Column(CLOB, nullable=True)
    URL = Column(String(500), nullable=True)
    ZAKRES_TEMATOW = Column(CLOB, nullable=True)
    ZAKRES_TEMATOW_ANG = Column(CLOB, nullable=True)
    METODY_DYD = Column(CLOB, nullable=True)
    METODY_DYD_ANG = Column(CLOB, nullable=True)
    LITERATURA = Column(CLOB, nullable=True)
    LITERATURA_ANG = Column(CLOB, nullable=True)
    CZY_POKAZYWAC_TERMIN = Column(String(1), nullable=False, default='T')

    groups = relationship(
        "Group",
        back_populates="didactic_cycle_class",
        primaryjoin="Group.GR_ZAJ_CYK_ID == DidacticCycleClasses.ID"
    )
    subject_cycle = relationship(  # MANYTOONE
        "SubjectCycle",
        back_populates="didactic_cycle_classes",
        primaryjoin="and_(foreign(DidacticCycleClasses.CDYD_KOD) == SubjectCycle.CDYD_KOD, "
                    "foreign(DidacticCycleClasses.PRZ_KOD) == SubjectCycle.PRZ_KOD)"
    )
    class_type = relationship(
        "ClassType",
        back_populates="didactic_cycle_classes",
        foreign_keys=[TZAJ_KOD]
    )
    __table_args__ = (
        Index('ZAJ_CYK_PK', 'ID', unique=True),
        Index('ZAJ_CYK_PRZ_CKL_FK_I', 'CDYD_KOD', 'PRZ_KOD'),
        Index('ZAJ_CYK_TZAJ_FK_I', 'TZAJ_KOD'),
        Index('ZAJ_CYK_UK', 'CDYD_KOD', 'PRZ_KOD', 'TZAJ_KOD', unique=True),
        Index('ZAJ_TPROT_FK_I', 'TPRO_KOD')
    )
class Group(Base):
    __tablename__ = 'DZ_GRUPY'

    ZAJ_CYK_ID = Column(Integer, ForeignKey('DZ_CYKLE_DYDAKTYCZNE.KOD'), primary_key=True, index=True)
    NR = Column(Integer, primary_key=True, index=True)
    LIMIT_MIEJSC = Column(Integer, nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    GR_NR = Column(Integer, nullable=True)
    GR_ZAJ_CYK_ID = Column(Integer, ForeignKey('DZ_ZAJECIA_CYKLI.ID'), nullable=True)
    OPIS = Column(String(1000), nullable=True)
    WAGA_PENSUM = Column(Float, nullable=True)
    ZAKRES_TEMATOW = Column(Text, nullable=True)
    ZAKRES_TEMATOW_ANG = Column(Text, nullable=True)
    METODY_DYD = Column(Text, nullable=True)
    METODY_DYD_ANG = Column(Text, nullable=True)
    LITERATURA = Column(Text, nullable=True)
    LITERATURA_ANG = Column(Text, nullable=True)
    URL = Column(String(500), nullable=True)
    OPIS_ANG = Column(String(1000), nullable=True)
    DOLNY_LIMIT_MIEJSC = Column(Integer, nullable=True)
    KRYTERIA_OCENIANIA = Column(Text, nullable=True)
    KRYTERIA_OCENIANIA_ANG = Column(Text, nullable=True)

    parent_group_id = Column(Integer, ForeignKey('DZ_GRUPY.ZAJ_CYK_ID'), nullable=True)
    parent_group_nr = Column(Integer, ForeignKey('DZ_GRUPY.NR'), nullable=True)

    parent_group = relationship(
        "Group",
        remote_side=[ZAJ_CYK_ID, NR],
        back_populates="subgroups",
        foreign_keys=[parent_group_id, parent_group_nr],  # Explicitly specify foreign keys
        primaryjoin="and_(Group.parent_group_id == Group.ZAJ_CYK_ID, Group.parent_group_nr == Group.NR)"  # Explicit join condition
    )

    subgroups = relationship(
        "Group",
        back_populates="parent_group",
        foreign_keys=[parent_group_id, parent_group_nr],  # Explicitly specify foreign keys
        primaryjoin="and_(Group.parent_group_id == Group.ZAJ_CYK_ID, Group.parent_group_nr == Group.NR)"  # Explicit join condition
    )

    didactic_cycle_class = relationship(
        "DidacticCycleClasses",
        back_populates="groups",
        primaryjoin="Group.GR_ZAJ_CYK_ID == DidacticCycleClasses.ID"
    )
    didactic_cycle = relationship(
        "DidacticCycles",
        back_populates="groups"
    )

    instructors = relationship(
    "GroupInstructor",
    back_populates="group",
    foreign_keys="[GroupInstructor.ZAJ_CYK_ID, GroupInstructor.GR_NR]",
    primaryjoin="and_(Group.ZAJ_CYK_ID == GroupInstructor.ZAJ_CYK_ID, Group.NR == GroupInstructor.GR_NR)",
    overlaps="didactic_cycle,subgroups"
    )

    __table_args__ = (
        Index('GR_GR_FK_I', 'GR_ZAJ_CYK_ID', 'GR_NR'),
        Index('GR_PK', 'ZAJ_CYK_ID', 'NR', unique=True),
        Index('GR_ZAJ_CYK_FK_I', 'ZAJ_CYK_ID')
    )
    

class GroupInstructor(Base):
    __tablename__ = 'DZ_PROWADZACY_GRUP'

    PRAC_ID = Column(Integer, ForeignKey('DZ_PRACOWNICY.ID'), primary_key=True, index=True)
    ZAJ_CYK_ID = Column(Integer, ForeignKey('DZ_GRUPY.ZAJ_CYK_ID'), primary_key=True, index=True)
    GR_NR = Column(Integer, ForeignKey('DZ_GRUPY.NR'), primary_key=True, index=True)
    WAGA_PENSUM = Column(Float, nullable=True)
    JEDN_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=False)
    LICZBA_GODZ = Column(Float, nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    LICZBA_GODZ_DO_PENSUM = Column(Float, nullable=True)
    CZY_ANKIETY = Column(String(1), nullable=False)
    CZY_PROTOKOLY = Column(String(1), nullable=False)
    LICZBA_GODZ_PRZEN = Column(Float, nullable=True)
    KOMENTARZ = Column(String(3000), nullable=True)
    PLAN_LICZBA_GODZ = Column(Float, nullable=True)
    PLAN_LICZBA_GODZ_DO_PENSUM = Column(Float, nullable=True)

    group = relationship(
    "Group",
    back_populates="instructors",
    foreign_keys=[ZAJ_CYK_ID, GR_NR],
    primaryjoin="and_(GroupInstructor.ZAJ_CYK_ID == Group.ZAJ_CYK_ID, GroupInstructor.GR_NR == Group.NR)",
    remote_side=[Group.ZAJ_CYK_ID, Group.NR]
    )
    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="group_instructors",
        foreign_keys=[JEDN_KOD]
    )
    instructor = relationship(
    "Employee",
    back_populates="group_instructors",
    overlaps="employee"
)
    instructor_employments = relationship(
    "InstructorEmployment",
    back_populates="group_instructor",
    foreign_keys="[InstructorEmployment.PRAC_ID, InstructorEmployment.ZAJ_CYK_ID, InstructorEmployment.GR_NR]",
    primaryjoin="and_(GroupInstructor.PRAC_ID == InstructorEmployment.PRAC_ID, "
                "GroupInstructor.ZAJ_CYK_ID == InstructorEmployment.ZAJ_CYK_ID, "
                "GroupInstructor.GR_NR == InstructorEmployment.GR_NR)"
    )
    employee = relationship(
    "Employee",
    back_populates="group_instructors",
    overlaps="instructor"
)

    __table_args__ = (
        Index('PRW_GR_GR_FK_I', 'ZAJ_CYK_ID', 'GR_NR'),
        Index('PRW_GR_PK', 'PRAC_ID', 'ZAJ_CYK_ID', 'GR_NR', unique=True),
        Index('PRW_GR_PRAC_FK_I', 'PRAC_ID')
    )

class StanowiskaZatrPensum(Base):
    __tablename__ = 'DZ_STANOWISKA_ZATR_PENSUM'

    ID = Column(Integer, primary_key=True, index=True)
    STAN_ID = Column(Integer, ForeignKey('DZ_STANOWISKA_ZATR.ID'), nullable=False)
    CDYD_POCZ = Column(String(20), ForeignKey('DZ_CYKLE_DYDAKTYCZNE.KOD'), nullable=False)
    PENSUM = Column(Integer, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    JED_ORG_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=True)
    CDYD_KON = Column(String(20), ForeignKey('DZ_CYKLE_DYDAKTYCZNE.KOD'), nullable=True)
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())

    cycle_end = relationship(
        "DidacticCycles",
        back_populates="positions_pensum_end",
        foreign_keys=[CDYD_KON]
    )
    cycle_start = relationship(
        "DidacticCycles",
        back_populates="positions_pensum_start",
        foreign_keys=[CDYD_POCZ]
    )
    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="positions_pensum",
        foreign_keys=[JED_ORG_KOD]
    )
    position = relationship(
        "Position",
        back_populates="positions_pensum",
        foreign_keys=[STAN_ID]
    )

    __table_args__ = (
        Index('STAN_PENS_PK', 'ID', unique=True),
        Index('STAN_PENS_STAN_FK_I', 'STAN_ID'),
        Index('STAN_PENS_CDYD_POCZ_FK_I', 'CDYD_POCZ'),
        Index('STAN_PENS_CDYD_KON_FK_I', 'CDYD_KON'),
        Index('STAN_PENS_JED_ORG_FK_I', 'JED_ORG_KOD'),
        Index('STAN_PENS_UK', 'STAN_ID', 'CDYD_POCZ', 'JED_ORG_KOD', unique=True)
    )

class Committee(Base):
    __tablename__ = 'DZ_KOMISJE'

    ID = Column(Integer, primary_key=True, index=True)
    TYPK_KOD = Column(String(20), ForeignKey('DZ_TYPY_KOMISJI.KOD'), nullable=False)
    DATA_POCZ = Column(Date, nullable=True)
    DATA_KON = Column(Date, nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    NAZWA = Column(String(200), nullable=True)
    JED_ORG_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=False)
    PROT_ID = Column(Integer, ForeignKey('DZ_TERMINY_PROTOKOLOW.PROT_ID'), nullable=True)
    TERM_PROT_NR = Column(Integer, ForeignKey('DZ_TERMINY_PROTOKOLOW.NR'), nullable=True)
    CZY_PUBLICZNA = Column(String(1), nullable=False)
    NAZWA_ANG = Column(String(200), nullable=True)

    committee_members = relationship(
        "CommitteeMember",
        back_populates="committee",
        foreign_keys="[CommitteeMember.KOMI_ID]"
    )
    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="committees",
        foreign_keys=[JED_ORG_KOD]
    )
    committee_type = relationship(
        "CommitteeType",
        back_populates="committees",
        foreign_keys=[TYPK_KOD]
    )

    __table_args__ = (
        Index('KOMI_JED_ORG_FK_I', 'JED_ORG_KOD'),
        Index('KOMI_PK', 'ID', unique=True),
        Index('KOMI_TERM_PROT_FK_I', 'PROT_ID', 'TERM_PROT_NR'),
        Index('KOMI_TYPK_FK_I', 'TYPK_KOD')
    )

class IndividualRates(Base):
    __tablename__ = 'DZ_INDYWIDUALNE_STAWKI'

    ID = Column(Integer, primary_key=True, index=True)
    RPENS_KOD = Column(String(20), ForeignKey('DZ_ROZLICZENIA_PENSUM.KOD'), nullable=False)
    PRAC_ID = Column(Integer, ForeignKey('DZ_PRACOWNICY.ID'), nullable=False)
    STAWKA = Column(Float, nullable=False)
    RODZAJ = Column(String(1), nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    PRZ_KOD = Column(String(20), ForeignKey('DZ_PRZEDMIOTY.KOD'), nullable=True)
    TZAJ_KOD = Column(String(20), ForeignKey('DZ_TYPY_ZAJEC.KOD'), nullable=True)
    UWAGI = Column(String(500), nullable=True)

    employee = relationship(
        "Employee",
        back_populates="individual_rates",
        foreign_keys=[PRAC_ID]
    )
    subject = relationship(
        "Subject",
        back_populates="individual_rates",
        foreign_keys=[PRZ_KOD]
    )
    pensum_settlement = relationship(
        "PensumSettlement",
        back_populates="individual_rates",
        foreign_keys=[RPENS_KOD]
    )
    class_type = relationship(
        "ClassType",
        back_populates="individual_rates",
        foreign_keys=[TZAJ_KOD]
    )
    __table_args__ = (
        Index('IND_STAW_PK', 'ID', unique=True),
        Index('IND_STAW_PRAC_FK_I', 'PRAC_ID'),
        Index('IND_STAW_PRZ_FK_I', 'PRZ_KOD'),
        Index('IND_STAW_RPENS_FK_I', 'RPENS_KOD'),
        Index('IND_STAW_TZAJ_FK_I', 'TZAJ_KOD')
    )

class Employee(Base):
    __tablename__ = 'DZ_PRACOWNICY'
    ID = Column(Integer, primary_key=True, index=True)
    OS_ID = Column(Integer, ForeignKey('DZ_OSOBY.ID'), nullable=False, unique=True)
    PIERWSZE_ZATR = Column(String(1), nullable=False)
    NR_AKT = Column(String(20), nullable=True, unique=True)
    NR_KARTY = Column(String(100), nullable=True)
    TELEFON1 = Column(String(30), nullable=True)
    TELEFON2 = Column(String(30), nullable=True)
    BADANIA_OKRESOWE = Column(Date, nullable=True)
    KONS_DO_ZMIANY = Column(String(1), nullable=True)
    KONSULTACJE = Column(String(1000), nullable=True)
    ZAINTERESOWANIA = Column(String(1000), nullable=True)
    ZAINTERESOWANIA_ANG = Column(String(1000), nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    EMERYTURA_DATA = Column(Date, nullable=True)
    DATA_NADANIA_TYTULU = Column(Date, nullable=True)
    AKTYWNY = Column(String(1), nullable=False, default='T')
    DATA_PRZESWIETLENIA = Column(Date, nullable=True)
    SL_ID = Column(Integer, ForeignKey('DZ_SALE.ID'), nullable=True)
    TYTUL_DDZ_ID = Column(Integer, ForeignKey('DZ_DZIEDZINY.ID'), nullable=True)
    DATA_SZKOLENIA_BHP = Column(Date, nullable=True)
    TYTUL_SZK_ID = Column(Integer, ForeignKey('DZ_SZKOLY.ID'), nullable=True)

    individual_rates = relationship(
        "IndividualRates",
        back_populates="employee",
        foreign_keys="[IndividualRates.PRAC_ID]"
    )
    employee_pensum = relationship(
        "EmployeePensum",
        back_populates="employee",
        foreign_keys="[EmployeePensum.PRAC_ID]"
    )
    person = relationship(
        "Person",
        back_populates="employees",
        foreign_keys=[OS_ID]
    )
    employments = relationship(
        "Employment",
        back_populates="employee",
        foreign_keys="[Employment.PRAC_ID]"
    )
    group_instructors = relationship(
        "GroupInstructor",
        back_populates="employee",
        foreign_keys="[GroupInstructor.PRAC_ID]"
    )
    external_pensum = relationship(
        "ExternalPensum",
        back_populates="employee",
        foreign_keys="[ExternalPensum.PRAC_ID]"
    )
    discounts = relationship(
        "Discount",
        back_populates="employee",
        foreign_keys="[Discount.PRAC_ID]"
    )

    __table_args__ = (
        CheckConstraint("PIERWSZE_ZATR IN ('T', 'N')", name='check_pierwsze_zatr'),
        CheckConstraint("KONS_DO_ZMIANY IN ('N', 'T')", name='check_kons_do_zmiany'),
        CheckConstraint("AKTYWNY IN ('N', 'T')", name='check_aktywny'),
        Index('PRAC_DDZ_FK_I', 'TYTUL_DDZ_ID'),
        Index('PRAC_NR_AKT_UK', 'NR_AKT', unique=True),
        Index('PRAC_OS_ID_UK', 'OS_ID', unique=True),
        Index('PRAC_PK', 'ID', unique=True),
        Index('PRAC_SL_FK_I', 'SL_ID'),
        Index('PRAC_TYTUL_SZK_FK_I', 'TYTUL_SZK_ID')
    )

class EmployeePensum(Base):
    __tablename__ = 'DZ_PENSUM_PRAC'

    PRAC_ID = Column(Integer, ForeignKey('DZ_PRACOWNICY.ID'), primary_key=True, index=True)
    RPENS_KOD = Column(String(20), ForeignKey('DZ_ROZLICZENIA_PENSUM.KOD'), primary_key=True, index=True)
    PENSUM = Column(Integer, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate()) 
    KOMENTARZ = Column(String(200), nullable=True)
    STATUS = Column(String(1), nullable=False, default='P')

    employee = relationship(
        "Employee",
        back_populates="employee_pensum",
        foreign_keys=[PRAC_ID]
    )
    pensum_settlement = relationship(
        "PensumSettlement",
        back_populates="employee_pensum",
        foreign_keys=[RPENS_KOD]
    )

    __table_args__ = (
        CheckConstraint("STATUS IN ('P', 'Z', 'X')", name='check_status'),
        Index('PENSP_PK', 'PRAC_ID', 'RPENS_KOD', unique=True),
    )

class ClassType(Base):
    __tablename__ = 'DZ_TYPY_ZAJEC'

    KOD = Column(String(20), primary_key=True, index=True)
    OPIS = Column(String(100), nullable=False)
    DESCRIPTION = Column(String(100), nullable=True)
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    UTW_ID = Column(String(30), nullable=False, default=func.user())

    individual_rates = relationship(
        "IndividualRates",
        back_populates="class_type",
        foreign_keys="[IndividualRates.TZAJ_KOD]"
    )
    conversion_values = relationship(
        "ConversionValue",
        back_populates="class_type",
        foreign_keys="[ConversionValue.TZAJ_KOD]"
    )
    didactic_cycle_classes = relationship(
        "DidacticCycleClasses",
        back_populates="class_type",
        foreign_keys=[DidacticCycleClasses.TZAJ_KOD]
    )

    __table_args__ = (
        Index('TZAJ_PK', 'KOD', unique=True),
    )

class OrganizationalUnits(Base):
    __tablename__ = 'DZ_JEDNOSTKI_ORGANIZACYJNE'

    KOD = Column(String(20), primary_key=True, index=True)
    TJEDN_KOD = Column(String(20), ForeignKey('DZ_TYPY_JEDNOSTEK.KOD'), nullable=False)
    OPIS = Column(String(200), nullable=False)
    OPIS_ANG = Column(String(200), nullable=True)
    JED_ORG_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=True)
    CZY_DYDAKTYCZNA = Column(String(1), nullable=False)
    CZY_ZATRUDNIA = Column(String(1), nullable=False)
    INST_WWW_KOD = Column(String(20), ForeignKey('DZ_INSTALACJE_WWW.KOD'), nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    CZY_PRZYZNAJE_AKADEMIKI = Column(String(1), nullable=False)
    SKROT_NAZWY = Column(String(20), nullable=True)
    OPIS_DO_SUPLEMENTU = Column(String(2000), nullable=True)
    OPIS_DO_SUPLEMENTU_ANG = Column(String(2000), nullable=True)
    ADRES_WWW = Column(String(200), nullable=True)
    CZY_WYSWIETLAC = Column(String(1), nullable=False)
    OPIS_NIE = Column(String(200), nullable=True)
    OPIS_ROS = Column(String(200), nullable=True)
    OPIS_HIS = Column(String(200), nullable=True)
    OPIS_FRA = Column(String(200), nullable=True)
    CZY_ARCHIWIZUJE = Column(String(1), nullable=False)
    ARCH_NR_DOPLYWU_S = Column(Integer, nullable=True)
    ARCH_NR_DOPLYWU_D = Column(Integer, nullable=True)
    ARCH_NR_DOPLYWU_H = Column(Integer, nullable=True)
    ARCH_NR_DOPLYWU_P = Column(Integer, nullable=True)
    DATA_ZALOZENIA = Column(Date, nullable=True)
    REGON = Column(String(14), nullable=True)
    CZY_ZAMIEJSCOWA = Column(String(1), nullable=False)
    CZY_PODSTAWOWA = Column(String(1), nullable=False)
    KOD_POLON = Column(String(50), nullable=True)
    ZDJECIE_BLOB_ID = Column(Integer, ForeignKey('DZ_BLOBY.ID'), nullable=True)
    LOGO_BLOB_ID = Column(Integer, ForeignKey('DZ_BLOBY.ID'), nullable=True)
    MPK = Column(String(100), nullable=True)
    SKROT_DO_JRWA = Column(String(20), nullable=True)
    EMAIL = Column(String(100), nullable=True)
    INFOKARTA_ID_BLOBBOX = Column(String(20), nullable=True)
    INFOKARTA_UWAGI = Column(String(200), nullable=True)
    GUID = Column(String(32), nullable=False, unique=True, default=func.rawtohex(func.sys_guid()))
    UID_POLON = Column(String(128), nullable=True)
    DATA_DO = Column(Date, nullable=True)
    UUID_POLON = Column(String(128), nullable=True)
    KOD_HR = Column(String(50), nullable=True)

    committee_functions_pensum = relationship(
        "CommitteeFunctionPensum",
        back_populates="organizational_unit",
        foreign_keys="[CommitteeFunctionPensum.JED_ORG_KOD]"
    )
    parent_unit = relationship(
        "OrganizationalUnits",
        back_populates="child_units",
        remote_side=[KOD],
        foreign_keys=[JED_ORG_KOD]
    )
    child_units = relationship(
        "OrganizationalUnits",
        back_populates="parent_unit",
        foreign_keys="[OrganizationalUnits.JED_ORG_KOD]"
    )
    committees = relationship(
        "Committee",
        back_populates="organizational_unit",
        foreign_keys="[Committee.JED_ORG_KOD]"
    )
    persons_social = relationship(
        "Person",
        back_populates="social_unit",
        foreign_keys="[Person.GDZIE_SOCJALNE]"
    )
    persons = relationship(
        "Person",
        back_populates="organizational_unit",
        foreign_keys="[Person.JED_ORG_KOD]"
    )
    employments = relationship(
        "Employment",
        back_populates="organizational_unit",
        foreign_keys="[Employment.JEDN_KOD]"
    )
    sub_employments = relationship(
        "Employment",
        back_populates="sub_organizational_unit",
        foreign_keys="[Employment.POD_JEDN_KOD]"
    )
    group_instructors = relationship(
        "GroupInstructor",
        back_populates="organizational_unit",
        foreign_keys="[GroupInstructor.JEDN_KOD]"
    )
    subjects_received = relationship(
        "Subject",
        back_populates="receiving_organizational_unit",
        foreign_keys="[Subject.JED_ORG_KOD_BIORCA]"
    )
    subjects = relationship(
        "Subject",
        back_populates="organizational_unit",
        foreign_keys="[Subject.JED_ORG_KOD]"
    )
    pensum_settlements = relationship(
        "PensumSettlement",
        back_populates="organizational_unit",
        foreign_keys="[PensumSettlement.JEDN_KOD]"
    )
    positions_pensum = relationship(
        "StanowiskaZatrPensum",
        back_populates="organizational_unit",
        foreign_keys="[StanowiskaZatrPensum.JED_ORG_KOD]"
    )
    field_of_study_authorizations = relationship(
        "FieldOfStudyAuthorization",
        back_populates="organizational_unit",
        foreign_keys="[FieldOfStudyAuthorization.JED_ORG_KOD]"
    )
    instructor_employments = relationship(
        "InstructorEmployment",
        back_populates="organizational_unit",
        foreign_keys="[InstructorEmployment.JEDN_KOD]"
    )

    __table_args__ = (
        CheckConstraint("regexp_instr(KOD, '\\||''|&|%') = 0", name='check_kod'),
        Index('JED_ORG_GUID_UK', 'GUID', unique=True),
        Index('JED_ORG_INST_WWW_FK_I', 'INST_WWW_KOD'),
        Index('JED_ORG_JED_ORG_FK_I', 'JED_ORG_KOD'),
        Index('JED_ORG_LOGO_BLOB_FK_I', 'LOGO_BLOB_ID'),
        Index('JED_ORG_OPIS_I', 'OPIS'),
        Index('JED_ORG_PK', 'KOD', unique=True),
        Index('JED_ORG_TJED_FK_I', 'TJEDN_KOD'),
        Index('JED_ORG_ZDJECIE_BLOB_FK_I', 'ZDJECIE_BLOB_ID')
    )

class Employment(Base):
    __tablename__ = 'DZ_PRAC_ZATR'

    ID = Column(Integer, primary_key=True, index=True)
    JEDN_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=False)
    PRAC_ID = Column(Integer, ForeignKey('DZ_PRACOWNICY.ID'), nullable=False)
    STAN_ID = Column(Integer, ForeignKey('DZ_STANOWISKA_ZATR.ID'), nullable=False)
    ETAT = Column(Float, nullable=False)
    FORM_KOD = Column(String(20), ForeignKey('DZ_FORMY_ZATR.KOD'), nullable=False)
    UMOWA_POCZ = Column(Date, nullable=False)
    UMOWA_KON = Column(Date, nullable=True)
    UWAGI = Column(String(500), nullable=True)
    POD_JEDN_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    UMOWA_PODSTAWOWA = Column(Integer, ForeignKey('DZ_PRAC_ZATR.ID'), nullable=False)
    UMOWA_POPRZEDNIA = Column(Integer, ForeignKey('DZ_PRAC_ZATR.ID'), nullable=True)
    ETAT_LICZNIK = Column(Integer, nullable=True)
    ETAT_MIANOWNIK = Column(Integer, nullable=True)
    DATA_OBJECIA_STAN = Column(Date, nullable=True)
    CZY_PODSTAWOWE = Column(String(1), nullable=False)
    KOD_HR = Column(String(50), nullable=True)
    DATA_NAWIAZANIA_SP = Column(Date, nullable=True)
    STATUS = Column(String(1), nullable=True)
    UID_POLON = Column(String(128), nullable=True)

    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="employments",
        foreign_keys=[JEDN_KOD]
    )
    sub_organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="sub_employments",
        foreign_keys=[POD_JEDN_KOD]
    )
    employee = relationship(
        "Employee",
        back_populates="employments",
        foreign_keys=[PRAC_ID]
    )
    position = relationship(
        "Position",
        back_populates="employments",
        foreign_keys=[STAN_ID]
    )
    base_contract = relationship(
        "Employment",
        back_populates="sub_contracts",
        remote_side=[ID],
        foreign_keys=[UMOWA_PODSTAWOWA]
    )
    sub_contracts = relationship(
        "Employment",
        back_populates="base_contract",
        foreign_keys="[Employment.UMOWA_PODSTAWOWA]"
    )
    previous_contract = relationship(
        "Employment",
        back_populates="next_contracts",
        remote_side=[ID],
        foreign_keys=[UMOWA_POPRZEDNIA]
    )
    next_contracts = relationship(
        "Employment",
        back_populates="previous_contract",
        foreign_keys="[Employment.UMOWA_POPRZEDNIA]"
    )
    instructor_employments = relationship(
        "InstructorEmployment",
        back_populates="employment",
        foreign_keys="[InstructorEmployment.PRACZ_ID]"
    )

    __table_args__ = (
        Index('PRACZ_FORM_FK_I', 'FORM_KOD'),
        Index('PRACZ_JED_ORG_FK2_I', 'POD_JEDN_KOD'),
        Index('PRACZ_JED_ORG_FK_I', 'JEDN_KOD'),
        Index('PRACZ_PK', 'ID', unique=True),
        Index('PRACZ_PRAC_FK_I', 'PRAC_ID'),
        Index('PRACZ_STAN_FK_I', 'STAN_ID'),
        Index('PRACZ_UPODST_FK_I', 'UMOWA_PODSTAWOWA'),
        Index('PRACZ_UPOPRZ_FK_I', 'UMOWA_POPRZEDNIA')
    )

class ThesisSupervisors(Base):
    __tablename__ = 'DZ_OPIEKUNOWIE_PRAC'

    OS_ID = Column(Integer, ForeignKey('DZ_OSOBY.ID'), primary_key=True, index=True)
    CERT_ID = Column(Integer, primary_key=True, index=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    ROLA = Column(String(1), nullable=True)
    LICZBA_GODZ_ZA_PRACE = Column(Float, nullable=True)
    LICZBA_GODZ_DO_PENSUM = Column(Float, nullable=True)
    RPENS_KOD = Column(String(20), ForeignKey('DZ_ROZLICZENIA_PENSUM.KOD'), nullable=True)
    PRZEL_KOD = Column(String(20), ForeignKey('DZ_PRZELICZNIKI.PRZEL_KOD'), nullable=True)
    LICZBA_GODZ_PRZEN = Column(Float, nullable=True)

    person = relationship(
        "Person",
        back_populates="thesis_supervisors",
        foreign_keys=[OS_ID]
    )
    conversion_rate = relationship(
        "ConversionRate",
        back_populates="thesis_supervisors",
        foreign_keys=[RPENS_KOD, PRZEL_KOD]
    )
    pensum_settlement = relationship(
        "PensumSettlement",
        back_populates="thesis_supervisors",
        foreign_keys=[RPENS_KOD]
    )

    __table_args__ = (
        Index('OP_CERT_FK_I', 'CERT_ID'),
        Index('OP_PRAC_FK_I', 'OS_ID'),
        Index('OP_PRC_PK', 'OS_ID', 'CERT_ID', unique=True),
        Index('OP_PRZEL_FK_I', 'RPENS_KOD', 'PRZEL_KOD'),
        Index('OP_RPENS_FK_I', 'RPENS_KOD')
    )

class Subject(Base):
    __tablename__ = 'DZ_PRZEDMIOTY'

    KOD = Column(String(20), primary_key=True, index=True)
    NAZWA = Column(String(200), nullable=False)
    JED_ORG_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    TPRO_KOD = Column(String(20), ForeignKey('DZ_TYPY_PROTOKOLOW.KOD'), nullable=False)
    CZY_WIELOKROTNE = Column(Integer, nullable=False)
    NAME = Column(String(200), nullable=True)
    SKROCONY_OPIS = Column(String(1000), nullable=True)
    SHORT_DESCRIPTION = Column(String(1000), nullable=True)
    JED_ORG_KOD_BIORCA = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=False)
    JZK_KOD = Column(String(3), ForeignKey('DZ_JEZYKI.KOD'), nullable=True)
    KOD_SOK = Column(String(5), ForeignKey('DZ_KODY_SOKRATES.KOD'), nullable=True)
    OPIS = Column(CLOB, nullable=True)
    DESCRIPTION = Column(CLOB, nullable=True)
    LITERATURA = Column(CLOB, nullable=True)
    BIBLIOGRAPHY = Column(CLOB, nullable=True)
    EFEKTY_UCZENIA = Column(CLOB, nullable=True)
    EFEKTY_UCZENIA_ANG = Column(CLOB, nullable=True)
    KRYTERIA_OCENIANIA = Column(CLOB, nullable=True)
    KRYTERIA_OCENIANIA_ANG = Column(CLOB, nullable=True)
    PRAKTYKI_ZAWODOWE = Column(String(1000), nullable=True)
    PRAKTYKI_ZAWODOWE_ANG = Column(String(1000), nullable=True)
    URL = Column(String(500), nullable=True)
    KOD_ISCED = Column(String(5), ForeignKey('DZ_KODY_ISCED.KOD'), nullable=True)
    NAZWA_POL = Column(String(200), nullable=True)
    GUID = Column(String(32), nullable=False, unique=True, default=func.rawtohex(func.sys_guid()))
    KSZTALCENIE_NAUCZYCIELA = Column(String(1), nullable=False)

    individual_rates = relationship(
        "IndividualRates",
        back_populates="subject",
        foreign_keys="[IndividualRates.PRZ_KOD]"
    )
    receiving_organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="subjects_received",
        foreign_keys=[JED_ORG_KOD_BIORCA]
    )
    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="subjects",
        foreign_keys=[JED_ORG_KOD]
    )
    subject_cycles = relationship(
        "SubjectCycle",
        back_populates="subject",
        foreign_keys="[SubjectCycle.PRZ_KOD]"
    )
    conversion_rates = relationship(
        "SubjectConversionRate",
        back_populates="subject",
        foreign_keys="[SubjectConversionRate.PRZ_KOD]"
    )

   
    __table_args__ = (
        CheckConstraint("regexp_instr(KOD, '\\||''|&|%') = 0", name='check_kod'),
        Index('PRZ_GUID_UK', 'GUID', unique=True),
        Index('PRZ_JED_ORG_BIOR_FK_I', 'JED_ORG_KOD_BIORCA'),
        Index('PRZ_JED_ORG_FK_I', 'JED_ORG_KOD'),
        Index('PRZ_JZ_FK_I', 'JZK_KOD'),
        Index('PRZ_KISCED_FK_I', 'KOD_ISCED'),
        Index('PRZ_PK', 'KOD', unique=True),
        Index('PRZ_SOK_KOD_FK_I', 'KOD_SOK'),
        Index('PRZ_TPRO_FK_I', 'TPRO_KOD')
    )

class SubjectCycle(Base):
    __tablename__ = 'DZ_PRZEDMIOTY_CYKLI'

    CDYD_KOD = Column(String(20), ForeignKey('DZ_CYKLE_DYDAKTYCZNE.KOD'), primary_key=True, index=True)
    PRZ_KOD = Column(String(20), ForeignKey('DZ_PRZEDMIOTY.KOD'), primary_key=True, index=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    TPRO_KOD = Column(String(20), ForeignKey('DZ_TYPY_PROTOKOLOW.KOD'), nullable=False)
    URL = Column(String(500), nullable=True)
    UWAGI = Column(CLOB, nullable=True)
    NOTES = Column(CLOB, nullable=True)
    LITERATURA = Column(CLOB, nullable=True)
    LITERATURA_ANG = Column(CLOB, nullable=True)
    OPIS = Column(CLOB, nullable=True)
    OPIS_ANG = Column(CLOB, nullable=True)
    SKROCONY_OPIS = Column(String(2000), nullable=True)
    SKROCONY_OPIS_ANG = Column(String(2000), nullable=True)
    STATUS_SYLABUSU = Column(String(1), nullable=False)
    GUID = Column(String(32), nullable=False, unique=True, default=func.rawtohex(func.sys_guid()))
    KSZTALCENIE_NAUCZYCIELA = Column(String(1), nullable=False)

    cycle = relationship(
    "DidacticCycles",
    back_populates="subject_cycles",
    foreign_keys=[CDYD_KOD]
    )
    subject = relationship(
        "Subject",
        back_populates="subject_cycles",
        foreign_keys=[PRZ_KOD]
    )
    didactic_cycle_classes = relationship(  # ONETOMANY
        "DidacticCycleClasses",
        back_populates="subject_cycle",
        primaryjoin="and_(foreign(SubjectCycle.CDYD_KOD) == DidacticCycleClasses.CDYD_KOD, "
                    "foreign(SubjectCycle.PRZ_KOD) == DidacticCycleClasses.PRZ_KOD)"
    )
    __table_args__ = (
        Index('PRZCKL_CDYD_FK_I', 'CDYD_KOD'),
        Index('PRZCKL_GUID_UK', 'GUID', unique=True),
        Index('PRZCKL_PK', 'CDYD_KOD', 'PRZ_KOD', unique=True),
        Index('PRZCKL_PRZ_FK_I', 'PRZ_KOD'),
        Index('PRZCKL_TPRO_FK_I', 'TPRO_KOD')
    )

class ConversionRate(Base):
    __tablename__ = 'DZ_PRZELICZNIKI'

    RPENS_KOD = Column(String(20), ForeignKey('DZ_ROZLICZENIA_PENSUM.KOD'), primary_key=True, index=True)
    PRZEL_KOD = Column(String(20), primary_key=True, index=True)
    OPIS = Column(String(100), nullable=False)
    KOLEJNOSC = Column(Integer, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    UPR_KIER_ID = Column(Integer, ForeignKey('DZ_UPRAWNIENIA_DO_KIERUNKOW.ID'), nullable=True)

    committee_members = relationship(
            "CommitteeMember",
            back_populates="conversion_rate",
            foreign_keys="[CommitteeMember.RPENS_KOD, CommitteeMember.PRZEL_KOD]"
        )
    thesis_supervisors = relationship(
        "ThesisSupervisors",
        back_populates="conversion_rate",
        foreign_keys="[ThesisSupervisors.RPENS_KOD, ThesisSupervisors.PRZEL_KOD]"
    )
    subject_conversion_rates = relationship(
        "SubjectConversionRate",
        back_populates="conversion_rate",
        foreign_keys="[SubjectConversionRate.RPENS_KOD, SubjectConversionRate.PRZEL_KOD]"
    )
    pensum_settlement = relationship(
        "PensumSettlement",
        back_populates="conversion_rates",
        foreign_keys=[RPENS_KOD]
    )
    field_of_study_authorization = relationship(
        "FieldOfStudyAuthorization",
        back_populates="conversion_rates",
        foreign_keys=[UPR_KIER_ID]
    )
    reviewers = relationship(
        "Reviewer",
        back_populates="conversion_rate",
        foreign_keys="[Reviewer.RPENS_KOD, Reviewer.PRZEL_KOD]"
    )
    external_pensum = relationship(
        "ExternalPensum",
        back_populates="conversion_rate",
        foreign_keys="[ExternalPensum.RPENS_KOD, ExternalPensum.PRZEL_KOD]"
    )
    conversion_values = relationship(
        "ConversionValue",
        back_populates="conversion_rate",
        foreign_keys="[ConversionValue.RPENS_KOD, ConversionValue.PRZEL_KOD]"
    )

    __table_args__ = (
        Index('PRZEL_PK', 'RPENS_KOD', 'PRZEL_KOD', unique=True),
        Index('PRZEL_RPENS_FK_I', 'RPENS_KOD'),
        Index('PRZEL_UPR_KIER_FK_I', 'UPR_KIER_ID')
    )

class SubjectConversionRate(Base):
    __tablename__ = 'DZ_PRZELICZNIKI_PRZEDMIOTOW'

    RPENS_KOD = Column(String(20), ForeignKey('DZ_PRZELICZNIKI.RPENS_KOD'), primary_key=True, index=True)
    PRZ_KOD = Column(String(20), ForeignKey('DZ_PRZEDMIOTY.KOD'), primary_key=True, index=True)
    PRZEL_KOD = Column(String(20), ForeignKey('DZ_PRZELICZNIKI.PRZEL_KOD'), primary_key=True, index=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())

    subject = relationship(
        "Subject",
        back_populates="conversion_rates",
        foreign_keys=[PRZ_KOD]
    )
    conversion_rate = relationship(
        "ConversionRate",
        back_populates="subject_conversion_rates",
        foreign_keys=[RPENS_KOD, PRZEL_KOD]
    )

    __table_args__ = (
        Index('PRZEL_PRZ_PK', 'RPENS_KOD', 'PRZ_KOD', 'PRZEL_KOD', unique=True),
        Index('PRZEL_PRZ_PRZEL_FK_I', 'RPENS_KOD', 'PRZEL_KOD'),
        Index('PRZEL_PRZ_PRZ_FK_I', 'PRZ_KOD'),
        Index('PRZEL_PRZ_UK', 'RPENS_KOD', 'PRZ_KOD', unique=True)
    )

class DiscountType(Base):
    __tablename__ = 'DZ_RODZAJE_ZNIZEK'

    ID = Column(Integer, primary_key=True, index=True)
    NAZWA = Column(String(100), nullable=False, unique=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    CZY_AKTUALNE = Column(String(1), nullable=False)

    discounts = relationship(
        "Discount",
        back_populates="discount_type",
        foreign_keys="[Discount.RODZ_ZNIZ_ID]"
    )

    __table_args__ = (
        Index('RODZ_NAZWA_UK', 'NAZWA', unique=True),
        Index('RODZ_PK', 'ID', unique=True)
    )

class ExternalPensum(Base):
    __tablename__ = 'DZ_ROZL_PENSUM_ZEWN'

    ID = Column(Integer, primary_key=True, index=True)
    RPENS_KOD = Column(String(20), ForeignKey('DZ_ROZLICZENIA_PENSUM.KOD'), nullable=False)
    PRAC_ID = Column(Integer, ForeignKey('DZ_PRACOWNICY.ID'), nullable=False)
    LICZBA_GODZ = Column(Float, nullable=False)
    CDYD_KOD = Column(String(20), ForeignKey('DZ_CYKLE_DYDAKTYCZNE.KOD'), nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    ZAJECIA = Column(String(2000), nullable=True)
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    LICZBA_GODZ_DO_PENSUM = Column(Float, nullable=True)
    PRZELICZNIK = Column(Float, nullable=True)
    PRZEL_KOD = Column(String(20), ForeignKey('DZ_PRZELICZNIKI.PRZEL_KOD'), nullable=True)
    LICZBA_GODZ_PRZEN = Column(Float, nullable=True)

    cycle = relationship(
        "DidacticCycles",
        back_populates="external_pensum",
        foreign_keys=[CDYD_KOD]
    )
    employee = relationship(
        "Employee",
        back_populates="external_pensum",
        foreign_keys=[PRAC_ID]
    )
    conversion_rate = relationship(
        "ConversionRate",
        back_populates="external_pensum",
        foreign_keys=[RPENS_KOD, PRZEL_KOD]
    )
    pensum_settlement = relationship(
        "PensumSettlement",
        back_populates="external_pensum",
        foreign_keys=[RPENS_KOD]
    )

    __table_args__ = (
        Index('RPENS_ZEWN_PK', 'ID', unique=True),
        Index('RPENS_ZEWN_RPENS_FK_I', 'RPENS_KOD'),
        Index('RPENS_ZEWN_PRAC_FK_I', 'PRAC_ID'),
        Index('RPENS_ZEWN_CDYD_FK_I', 'CDYD_KOD'),
        Index('RPENS_ZEWN_PRZEL_FK_I', 'RPENS_KOD', 'PRZEL_KOD')
    )

class Discount(Base):
    __tablename__ = 'DZ_ZNIZKI_PENSUM'

    ID = Column(Integer, primary_key=True, index=True)
    PRAC_ID = Column(Integer, ForeignKey('DZ_PRACOWNICY.ID'), nullable=False)
    ZNIZKA = Column(Integer, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    RODZ_ZNIZ_ID = Column(Integer, ForeignKey('DZ_RODZAJE_ZNIZEK.ID'), nullable=False)
    RPENS_KOD = Column(String(20), ForeignKey('DZ_ROZLICZENIA_PENSUM.KOD'), nullable=False)
    TYP = Column(String(1), nullable=False)

    employee = relationship(
        "Employee",
        back_populates="discounts",
        foreign_keys=[PRAC_ID]
    )
    discount_type = relationship(
        "DiscountType",
        back_populates="discounts",
        foreign_keys=[RODZ_ZNIZ_ID]
    )
    pensum_settlement = relationship(
        "PensumSettlement",
        back_populates="discounts",
        foreign_keys=[RPENS_KOD]
    )

    __table_args__ = (
        Index('ZPENS_PK', 'ID', unique=True),
        Index('ZNIZ_PRAC_FK_I', 'PRAC_ID')
    )
class Reviewer(Base):
    __tablename__ = 'DZ_RECENZENCI_PRAC'

    ID = Column(Integer, primary_key=True, index=True)
    OS_ID = Column(Integer, ForeignKey('DZ_OSOBY.ID'), nullable=False)
    PRC_CERT_ID = Column(Integer, ForeignKey('DZ_PRACE_CERT.ID'), nullable=False)
    AUTOR_OS_ID = Column(Integer, ForeignKey('DZ_OSOBY.ID'), nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    LICZBA_GODZ_ZA_PRACE = Column(Float, nullable=True)
    LICZBA_GODZ_DO_PENSUM = Column(Float, nullable=True)
    RPENS_KOD = Column(String(20), ForeignKey('DZ_ROZLICZENIA_PENSUM.KOD'), nullable=True)
    PRZEL_KOD = Column(String(20), ForeignKey('DZ_PRZELICZNIKI.PRZEL_KOD'), nullable=True)
    LICZBA_GODZ_PRZEN = Column(Float, nullable=True)

    author = relationship(
        "Person",
        back_populates="authored_reviews",
        foreign_keys=[AUTOR_OS_ID]
    )
    person = relationship(
        "Person",
        back_populates="reviews",
        foreign_keys=[OS_ID]
    )
    conversion_rate = relationship(
        "ConversionRate",
        back_populates="reviewers",
        foreign_keys=[RPENS_KOD, PRZEL_KOD]
    )
    pensum_settlement = relationship(
        "PensumSettlement",
        back_populates="reviewers",
        foreign_keys=[RPENS_KOD]
    )

    __table_args__ = (
        Index('REC_PRAC_AUTOR_OS_FK_I', 'AUTOR_OS_ID'),
        Index('REC_PRAC_OS_FK_I', 'OS_ID'),
        Index('REC_PRAC_PK', 'ID', unique=True),
        Index('REC_PRAC_PRC_CERT_FK_I', 'PRC_CERT_ID'),
        Index('REC_PRAC_PRZEL_FK_I', 'RPENS_KOD', 'PRZEL_KOD'),
        Index('REC_PRAC_RPENS_FK_I', 'RPENS_KOD'),
        Index('REC_PRAC_UK', 'OS_ID', 'PRC_CERT_ID', 'AUTOR_OS_ID', unique=True)
    )

class ConversionValue(Base):
    __tablename__ = 'DZ_WARTOSCI_PRZELICZNIKOW'

    ID = Column(Integer, primary_key=True, index=True)
    RPENS_KOD = Column(String(20), ForeignKey('DZ_PRZELICZNIKI.RPENS_KOD'), nullable=False)
    PRZEL_KOD = Column(String(20), ForeignKey('DZ_PRZELICZNIKI.PRZEL_KOD'), nullable=False)
    STAN_ID = Column(Integer, ForeignKey('DZ_STANOWISKA_ZATR.ID'), nullable=True)
    TYTUL_ID = Column(Integer, ForeignKey('DZ_TYTULY.ID'), nullable=True)
    TZAJ_KOD = Column(String(20), ForeignKey('DZ_TYPY_ZAJEC.KOD'), nullable=True)
    STAWKA = Column(Float, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    RODZAJ = Column(String(1), nullable=True)

    conversion_rate = relationship(
        "ConversionRate",
        back_populates="conversion_values",
        foreign_keys=[RPENS_KOD, PRZEL_KOD]
    )
    position = relationship(
        "StanowiskaZatr",
        back_populates="conversion_values",
        foreign_keys=[STAN_ID]
    )
    title = relationship(
        "Title",
        back_populates="conversion_values",
        foreign_keys=[TYTUL_ID]
    )
    class_type = relationship(
        "ClassType",
        back_populates="conversion_values",
        foreign_keys=[TZAJ_KOD]
    )

   
    __table_args__ = (
        Index('WART_PRZEL_PK', 'ID', unique=True),
        Index('WART_PRZEL_PRZEL_FK_I', 'RPENS_KOD', 'PRZEL_KOD'),
        Index('WART_PRZEL_STAN_FK_I', 'STAN_ID'),
        Index('WART_PRZEL_TYTUL_FK_I', 'TYTUL_ID'),
        Index('WART_PRZEL_TZAJ_FK_I', 'TZAJ_KOD'),
        Index('WART_PRZEL_UK', 'RPENS_KOD', 'PRZEL_KOD', 'STAN_ID', 'TYTUL_ID', 'TZAJ_KOD', 'RODZAJ', unique=True)
    )  

class CommitteeType(Base):
    __tablename__ = 'DZ_TYPY_KOMISJI'

    KOD = Column(String(20), primary_key=True, index=True)
    NAZWA = Column(String(100), nullable=False, unique=True)
    UWAGI = Column(String(500), nullable=True)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    KLASA_KOMISJI = Column(String(1), nullable=False)

    committee_functions = relationship(
        "CommitteeFunction",
        back_populates="committee_type",
        foreign_keys="[CommitteeFunction.TYPK_KOD]"
    )
    committees = relationship(
        "Committee",
        back_populates="committee_type",
        foreign_keys="[Committee.TYPK_KOD]"
    )

    __table_args__ = (
        Index('TYPK_NAZWA_UK', 'NAZWA', unique=True),
        Index('TYPK_PK', 'KOD', unique=True)
    )

class Title(Base):
    __tablename__ = 'DZ_TYTULY'

    ID = Column(Integer, primary_key=True, index=True)
    NAZWA = Column(String(30), nullable=False)
    OPIS = Column(String(200), nullable=True)
    KOD_HR = Column(String(50), nullable=True, unique=True)
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    KOD_POLON = Column(String(20), nullable=True)

    persons_with_post_title = relationship(
        "Person",
        back_populates="post_title",
        foreign_keys="[Person.TYTUL_PO]"
    )
    persons_with_pre_title = relationship(
        "Person",
        back_populates="pre_title",
        foreign_keys="[Person.TYTUL_PRZED]"
    )
    conversion_values = relationship(
        "ConversionValue",
        back_populates="title",
        foreign_keys="[ConversionValue.TYTUL_ID]"
    )

    __table_args__ = (
        CheckConstraint("regexp_instr(KOD_HR, '\\||''|&|%') = 0", name='check_kod_hr'),
        Index('DZ_TYT_KOD_UK', 'KOD_HR', unique=True),
        Index('TYT_PK', 'ID', unique=True)
    )

class FieldOfStudyAuthorization(Base):
    __tablename__ = 'DZ_UPRAWNIENIA_DO_KIERUNKOW'

    ID = Column(Integer, primary_key=True, index=True)
    KOD_POLON = Column(String(20), nullable=False)
    JED_ORG_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=False)
    KRSTD_KOD = Column(String(20), nullable=False)
    STOPIEN_STUDIOW = Column(Integer, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    PROFIL = Column(String(2), nullable=True)
    STOP_ZAW_ID = Column(Integer, nullable=True)
    KOMENTARZ = Column(String(200), nullable=True)
    CZY_AKTUALNE = Column(String(1), nullable=False)
    POPRZEDNI_KOD_POLON = Column(String(20), nullable=True)
    UID_POLON = Column(String(128), nullable=True)

    conversion_rates = relationship(
        "ConversionRate",
        back_populates="field_of_study_authorization",
        foreign_keys="[ConversionRate.UPR_KIER_ID]"
    )
    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="field_of_study_authorizations",
        foreign_keys=[JED_ORG_KOD]
    )

    __table_args__ = (
        Index('UPR_KIER_JED_ORG_FK_I', 'JED_ORG_KOD'),
        Index('UPR_KIER_KRSTD_FK_I', 'KRSTD_KOD'),
        Index('UPR_KIER_PK', 'ID', unique=True),
        Index('UPR_KIER_STOP_ZAW_FK_I', 'STOP_ZAW_ID'),
        Index('UPR_KIER_UK', 'JED_ORG_KOD', 'KRSTD_KOD', 'STOPIEN_STUDIOW', 'PROFIL', 'STOP_ZAW_ID', 'KOMENTARZ', unique=True)
    )

class TypyProtokolow(Base):
    __tablename__ = 'DZ_TYPY_PROTOKOLOW'
    # Define columns here...
    ID = Column(Integer, primary_key=True, autoincrement=True)
   

class InstructorEmployment(Base):
    __tablename__ = 'DZ_ZATRUDNIENIA_PROWADZACYCH'

    ID = Column(Integer, primary_key=True, index=True)
    PRAC_ID = Column(Integer, ForeignKey('DZ_PROWADZACY_GRUP.PRAC_ID'), nullable=False)
    ZAJ_CYK_ID = Column(Integer, ForeignKey('DZ_PROWADZACY_GRUP.ZAJ_CYK_ID'), nullable=False)
    GR_NR = Column(Integer, ForeignKey('DZ_PROWADZACY_GRUP.GR_NR'), nullable=False)
    KOLEJNOSC = Column(Integer, nullable=False)
    LICZBA_GODZ = Column(Float, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    PRACZ_ID = Column(Integer, ForeignKey('DZ_PRAC_ZATR.ID'), nullable=True)
    PRACN_ID = Column(Integer, ForeignKey('DZ_PRAC_ZATR_NIEETAT.ID'), nullable=True)
    STAWKA = Column(Float, nullable=True)
    JEDN_KOD = Column(String(20), ForeignKey('DZ_JEDNOSTKI_ORGANIZACYJNE.KOD'), nullable=True)
    WAGA_PENSUM = Column(Float, nullable=True)
    LICZBA_GODZ_DO_PENSUM = Column(Float, nullable=True)
    LICZBA_GODZ_PRZEN = Column(Float, nullable=True)
    PLAN_LICZBA_GODZ = Column(Float, nullable=True)
    PLAN_LICZBA_GODZ_DO_PENSUM = Column(Float, nullable=True)
    UWAGI = Column(String(500), nullable=True)

    worked_hours = relationship(
        "WorkedHours",
        back_populates="instructor_employment",
        foreign_keys="[WorkedHours.ZATR_PROW_ID]"
    )
    organizational_unit = relationship(
        "OrganizationalUnits",
        back_populates="instructor_employments",
        foreign_keys=[JEDN_KOD]
    )
    group_instructor = relationship(
        "GroupInstructor",
        back_populates="instructor_employments",
        foreign_keys=[PRAC_ID, ZAJ_CYK_ID, GR_NR],  # Jawne określenie kluczy obcych
        primaryjoin="and_("
                    "InstructorEmployment.PRAC_ID == GroupInstructor.PRAC_ID, "
                    "InstructorEmployment.ZAJ_CYK_ID == GroupInstructor.ZAJ_CYK_ID, "
                    "InstructorEmployment.GR_NR == GroupInstructor.GR_NR)"
    )
    employment = relationship(
        "Employment",
        back_populates="instructor_employments",
        foreign_keys=[PRACZ_ID]
    )
   
    __table_args__ = (
        Index('ZATR_PROW_PK', 'ID', unique=True),
        Index('ZATR_PROW_JEDN_FK_I', 'JEDN_KOD'),
        Index('ZATR_PROW_NIEETAT_FK_I', 'PRACN_ID'),
        Index('ZATR_PROW_PROW_FK_I', 'PRAC_ID', 'ZAJ_CYK_ID', 'GR_NR'),
        Index('ZATR_PROW_ZATR_FK_I', 'PRACZ_ID')
    )

class PrzepracowaneGodziny(Base):
    __tablename__ = 'DZ_PRZEPRACOWANE_GODZINY'

    ID = Column(Integer, primary_key=True, index=True)
    ZATR_PROW_ID = Column(Integer, ForeignKey('DZ_ZATRUDNIENIA_PROWADZACYCH.ID'), nullable=False)
    MIESIAC = Column(Integer, nullable=False)
    ROK = Column(Integer, nullable=False)
    LICZBA_GODZ_PENSUM = Column(Float, nullable=False)
    LICZBA_GODZ_PONADWYM = Column(Float, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    UWAGI = Column(String(500), nullable=True)

    instructor_employment = relationship(
        "InstructorEmployment",
        back_populates="worked_hours",
        foreign_keys=[ZATR_PROW_ID]
    )

    __table_args__ = (
        CheckConstraint("MIESIAC BETWEEN 1 AND 12", name='check_miesiac'),
        Index('PRZEPR_GODZ_PK', 'ID', unique=True),
        Index('PRZEPR_GODZ_UK', 'ZATR_PROW_ID', 'MIESIAC', 'ROK', unique=True)
    )

class Position(Base):
    __tablename__ = 'DZ_STANOWISKA_ZATR'

    ID = Column(Integer, primary_key=True, index=True)
    NAZWA = Column(String(100), nullable=False)
    NAZWA_ANG = Column(String(100), nullable=True)
    GRUP_KOD = Column(String(20), ForeignKey('DZ_GRUPY_ZATR.KOD'), nullable=False)
    PENSUM_UCZELNIANE = Column(Integer, nullable=False)
    UTW_ID = Column(String(30), nullable=False, default=func.user())
    UTW_DATA = Column(Date, nullable=False, default=func.sysdate())
    MOD_ID = Column(String(30), nullable=False, default=func.user())
    MOD_DATA = Column(Date, nullable=False, default=func.sysdate())
    KOD = Column(String(20), nullable=True, unique=True)
    KOD_POLON = Column(String(100), nullable=True)

    employments = relationship(
        "Employment",
        back_populates="position",
        foreign_keys="[Employment.STAN_ID]"
    )
    positions_pensum = relationship(
        "StanowiskaZatrPensum",
        back_populates="position",
        foreign_keys="[StanowiskaZatrPensum.STAN_ID]"
    )
    conversion_values = relationship(
        "ConversionValue",
        back_populates="position",
        foreign_keys="[ConversionValue.STAN_ID]"
    )

    __table_args__ = (
        Index('DZ_STAN_ZATR_KOD_UK', 'KOD', unique=True),
        Index('STAN_GRUP_FK_I', 'GRUP_KOD'),
        Index('STAN_NAZWA_UK', 'NAZWA', 'GRUP_KOD', unique=True),
        Index('STAN_PK', 'ID', unique=True)
    )