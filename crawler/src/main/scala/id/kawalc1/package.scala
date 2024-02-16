package id

import com.typesafe.scalalogging.LazyLogging
import enumeratum.values.{ShortEnum, ShortEnumEntry}

import java.sql.Timestamp
import java.time.Instant
import java.util.UUID
import scala.collection.immutable
import scala.util.Try

package object kawalc1 extends LazyLogging {

  def formTypeToConfig(formType: FormType, plano: Option[Plano], halaman: Option[String]): String = (formType, plano, halaman) match {
    case (FormType.PPWP, Some(Plano.YES), Some("1")) =>
      "digit_config_ppwp_plano_halaman_1_2019.json,digit_config_pilpres_exact_smaller_2019.json"
    case (FormType.PPWP, Some(Plano.YES), Some("2")) =>
      "digit_config_pilpres_exact_smaller_2019.json,digit_config_ppwp_scan_halaman_2_2019.json"
    case (FormType.PPWP, Some(Plano.NO), Some("2")) =>
      "digit_config_ppwp_scan_halaman_2_2019.json,digit_config_ppwp_scan_halaman_1_2019.json"
    case (FormType.PPWP, Some(Plano.NO), Some("1")) =>
      "digit_config_ppwp_scan_halaman_1_2019.json,digit_config_ppwp_scan_halaman_2_2019.json"
    case _ =>
//      logger.error(s"Config not defined for $formType, $plano, $halaman")
      "pilpres_2024_plano_halaman2.json"
  }
  case class Problem(
      kelId: Int,
      kelName: String,
      tpsNo: Int,
      url: String,
      reason: String,
      ts: Int,
      response_code: Option[Int]
  )

  case class Approval(
      kelId: Int,
      kelName: String,
      tpsNo: Int,
      sum: Summary,
      imageId: String,
      c1: C1
  )

  case class ProblemReported(
      kelId: Int,
      kelName: String,
      tpsNo: Int,
      url: String,
      reason: String,
  )

  case class FormProcessed(
      kelId: Int,
      tpsNo: Int,
      url: String
  )

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

  case class ProbabilitiesResponse(
      probabilityMatrix: Seq[Seq[NumberSet]]
  )

  case class C1(
      plano: Option[Plano],
      `type`: FormType,
      halaman: Option[String]
  )

  case class VerificationOld(
      ts: Timestamp,
      c1: Option[C1],
      sum: Option[Summary],
      common: Common
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
      idKel: Long,
      nama: String
  )

  case class SingleOldTps(
      nama: String,
      photo: String,
      imageId: Option[String] = None,
      kelurahanId: Int,
      tpsId: Int,
      verification: VerificationOld
  )

  case class SingleTpsPhotoDao(
      kelurahanId: Long,
      tpsId: Int,
      name: String,
      idLokasi: String,
      uid: Option[String],
      updatedTs: Timestamp,
      uploadedPhotoId: String,
      uploadedPhotoUrl: String,
      dpt: Int,
      pas1: Option[Int],
      pas2: Option[Int],
      pas3: Option[Int],
      anyPendingTps: Option[String],
      totalTps: Int,
      totalPendingTps: Int,
      totalCompletedTps: Int,
      totalErrorTps: Int,
      formType: Option[Short],
      plano: Option[Short],
      halaman: Option[String],
      lastUpdated: Timestamp = Timestamp.from(Instant.now())
  )

  case class SingleTpsDao(
      kelurahanId: Long,
      tpsId: Int,
      name: String,
      idLokasi: String,
      uid: Option[String],
      updatedTs: Timestamp,
      uploadedPhotoId: Option[String],
      uploadedPhotoUrl: Option[String],
      dpt: Int,
      pas1: Option[Int],
      pas2: Option[Int],
      pas3: Option[Int],
      anyPendingTps: Option[String],
      totalTps: Int,
      totalPendingTps: Int,
      totalCompletedTps: Int,
      totalErrorTps: Int,
      lastUpdated: Timestamp = Timestamp.from(Instant.now())
  )

  case class TpsBasedData(
      withPhoto: Seq[SingleTpsPhotoDao],
      plain: Seq[SingleTpsDao]
  )

  case class TpsOldDto(photos: Map[String, VerificationOld])

  case class KelurahanOld(
      id: Int,
      name: String,
      parentNames: Seq[String],
      data: Map[Int, TpsOldDto]
  )

  case class KpuData(
      ts: String
  )

  case class UploadedPhoto(
      photoUrl: String,
      imageId: String,
      kpuData: Option[KpuData]
  )

  case class TpsInfo(
      pendingUploads: Option[Map[String, Object]],
      idLokasi: String,
      pas2: Int,
      totalTps: Int,
      pas3: Int,
      totalCompletedTps: Int,
      dpt: Option[Int],
      totalPendingTps: Int,
      anyPendingTps: Option[String],
      uid: Option[String],
      uploadedPhoto: Option[UploadedPhoto],
      name: String,
      totalErrorTps: Int,
      pas1: Int,
      updateTs: Long
  )

  case class Kelurahan(
      id: String,
      names: Seq[String],
      aggregated: Map[String, Seq[TpsInfo]]
  )

  case class KelurahanResponse(
      result: Kelurahan
  )

  case class MaybeKelurahanResponse(
      result: Option[Kelurahan],
      error: Boolean = false
  )

  object Kelurahan {

    private def explodeForPhotos(infos: Seq[TpsInfo]): Seq[TpsInfo] = {
      infos.flatMap { t =>
        val pendingPhotos: Seq[UploadedPhoto] = t.pendingUploads.toSeq.flatMap(_.flatMap {
          case (key, value) if value.toString != "true" => Some(UploadedPhoto(value.toString, key, None))
          case _                                        => None
        })
        val photos = pendingPhotos ++ t.uploadedPhoto
        photos.map(p => t.copy(uploadedPhoto = Some(p)))
      }

    }

    def toTps(kelurahan: KelurahanResponse): Seq[SingleTpsDao] = {
      (for {
        (_, infos) <- kelurahan.result.aggregated
      } yield {
        val t = infos.head
        SingleTpsDao(
          kelurahanId = kelurahan.result.id.toLong,
          tpsId = Try(t.name.toInt).getOrElse(t.idLokasi.last.toInt),
          name = kelurahan.result.names.mkString(", "),
          idLokasi = t.idLokasi,
          uid = t.uid,
          updatedTs = Timestamp.from(Instant.ofEpochMilli(t.updateTs)),
          uploadedPhotoId = t.uploadedPhoto.map(_.imageId),
          uploadedPhotoUrl = t.uploadedPhoto.map(_.photoUrl),
          dpt = t.dpt.getOrElse(0),
          pas1 = Some(t.pas1),
          pas2 = Some(t.pas2),
          pas3 = Some(t.pas3),
          anyPendingTps = t.anyPendingTps,
          totalTps = t.totalTps,
          totalPendingTps = t.totalPendingTps,
          totalCompletedTps = t.totalCompletedTps,
          totalErrorTps = t.totalErrorTps
        )
      }).toSeq
    }

    def toPhotoTps(kelurahan: KelurahanResponse): Seq[SingleTpsPhotoDao] = {
      for {
        tps        <- kelurahan.result.aggregated
        t: TpsInfo <- explodeForPhotos(tps._2)
        if t.uploadedPhoto.isDefined
      } yield {
        SingleTpsPhotoDao(
          kelurahanId = kelurahan.result.id.toLong,
          tpsId = t.name.toInt,
          name = kelurahan.result.names.mkString(", "),
          idLokasi = t.idLokasi,
          uid = t.uid,
          updatedTs = Timestamp.from(Instant.ofEpochMilli(t.updateTs)),
          uploadedPhotoId = t.uploadedPhoto
            .map(_.imageId)
            .getOrElse(throw new IllegalStateException(s"${t.idLokasi} ${t.name} does not have imageId")),
          uploadedPhotoUrl = t.uploadedPhoto
            .map(_.photoUrl)
            .getOrElse(throw new IllegalStateException(s"${t.idLokasi} ${t.name} does not have uploadedPhotoUrl")),
          dpt = t.dpt.getOrElse(0),
          pas1 = Some(t.pas1),
          pas2 = Some(t.pas2),
          pas3 = Some(t.pas3),
          anyPendingTps = t.anyPendingTps,
          totalTps = t.totalTps,
          totalPendingTps = t.totalPendingTps,
          totalCompletedTps = t.totalCompletedTps,
          totalErrorTps = t.totalErrorTps,
          formType = t.uploadedPhoto.flatMap(_.kpuData).map(_ => FormType.KPU.value),
          plano = Some(Plano.YES.value),
          halaman = None
        )
      }
    }.toSeq
  }

  object KelurahanOld {
    def toTps(kelurahan: KelurahanOld): Seq[SingleOldTps] = {
      for {
        tps   <- kelurahan.data
        photo <- tps._2.photos
      } yield SingleOldTps(kelurahan.name, photo._1, None, kelurahan.id, tps._1, photo._2)
    }.toSeq
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
      tSah: Int
  ) extends Summary

  case class Partai(
      name: String,
      amount: Int
  )

  case class SingleSum(
      jum: Int,
  ) extends Summary

  case class LegislativeSum(
      jum: Int,
  ) extends Summary

  case class Dpr(
      partai: String,
      votes: Int
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

    case object KPU extends FormType(0)

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
    "pkp",
    "pJum"
  )

  case class StringField(
      stringValue: String
  )

  case class IntField(
      integerValue: String
  )

  case class Fields(
      tpsNo: IntField,
      kelId: IntField,
      ts: IntField,
      kelName: StringField,
      url: StringField,
      reason: StringField
  )

  case class MapValue(
      fields: Fields
  )

  case class Report(
      mapValue: MapValue
  )

  object Report {
    def toProblemReported(report: Report): ProblemReported = {
      val f = report.mapValue.fields
      ProblemReported(
        f.kelId.integerValue.toInt,
        f.kelName.stringValue,
        f.tpsNo.integerValue.toInt,
        f.url.stringValue,
        f.reason.stringValue
      )
    }
  }
}
