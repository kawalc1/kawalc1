package id

import java.sql.Timestamp

import enumeratum.values.{ShortEnum, ShortEnumEntry}

import scala.collection.immutable

package object kawalc1 {

  def formTypeToConfig(formType: FormType) = formType match {
    case FormType.PPWP => "digit_config_pilpres_2019.json"
    case FormType.DPR  => ???
    case _             => ???
  }

  case class NumberSet(
      numbers: Seq[Numbers],
      confidence: Double
  )

  case class Numbers(
      id: String,
      number: Int,
      shortName: String,
      displayName: String
  )

  case class Probabilities(
      probabilityMatrix: Seq[Seq[NumberSet]]
  )

  case class C1(
      plano: Plano,
      `type`: FormType
  )

  case class Verification(
      ts: Timestamp,
      c1: Option[C1],
      sum: Option[Summary],
      common: Common
  )

  case class Common(
      cakupan: Option[Int],
      pending: Option[Int],
      error: Option[Int],
      janggal: Option[Int],
  )

  case class KelurahanId(
      idKel: Int,
      nama: String
  )

  case class SingleTps(
      nama: String,
      photo: String,
      kelurahanId: Int,
      tpsId: Int,
      verification: Verification
  )

  case class Tps(photos: Map[String, Verification])

  case class Kelurahan(
      id: Int,
      name: String,
      parentNames: Seq[String],
      data: Map[Int, Tps]
  )

  object Kelurahan {
    def toTps(kelurahan: Kelurahan) = {
      for {
        tps   <- kelurahan.data
        photo <- tps._2.photos
      } yield SingleTps(kelurahan.name, photo._1, kelurahan.id, tps._1, photo._2)
    }
  }

  trait Summary

  case class PresidentialLembar1(
      jum: Int,
      plano: Boolean
  ) extends Summary

  case class PresidentialLembar2(
      pas1: Int,
      pas2: Int,
      sah: Int,
      tSah: Int,
  ) extends Summary

  case class SingleSum(
      jum: Int,
  ) extends Summary

  case class LegislativeSum(
      jum: Int,
  ) extends Summary

  case class Dpr(
      votes: Map[String, Option[Int]],
  ) extends Summary

  case class Pending(
      cakupan: Int,
      pending: Int
  ) extends Summary

  sealed abstract class Plano(val value: Short) extends ShortEnumEntry

  case object Plano extends ShortEnum[Plano] {

    case object YES extends Plano(1)

    case object NO extends Plano(2)

    val values: immutable.IndexedSeq[Plano] = findValues
  }

  sealed abstract class FormType(val value: Short) extends ShortEnumEntry

  case object FormType extends ShortEnum[FormType] {

    // Full blown until digitized.
    case object PPWP extends FormType(1)

    case object DPR extends FormType(2)

    // Only up to halaman, not digitized.
    case object DPD extends FormType(3)

    case object DPRP extends FormType(4)

    case object DPRPB extends FormType(5)

    case object DPRA extends FormType(6)

    case object DPRD_PROV extends FormType(7)

    case object DPRD_KAB_KOTA extends FormType(8)

    case object DPRK extends FormType(9)

    // Up to choosing this type.
    case object OTHERS extends FormType(10)

    case object DELETED extends FormType(11)

    case object MALICIOUS extends FormType(12)

    val values: immutable.IndexedSeq[FormType] = findValues
  }

  val Parties = Seq(
    "pkb",
    "ger",
    "pdi",
    "gol",
    "nas",
    "gar",
    "ber",
    "sej",
    "per",
    "ppp",
    "psi",
    "pan",
    "han",
    "dem",
    "pa",
    "ps",
    "pda",
    "pna",
    "pbb",
    "pkp"
  )
}
