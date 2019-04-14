package id.kawalc1.database

import enumeratum.values.SlickValueEnumSupport
import slick.dbio.Effect
import slick.jdbc.SQLiteProfile.api._
import slick.lifted.Tag
import slick.sql.FixedSqlAction

case class AlignResult(
  id: Int,
  tps: Int,
  response: String,
  responseCode: Int,
  photo: String,
  photoSize: Int,
  alignQuality: Int,
  config: String,
  alignedUrl: Option[String],
  extracted: Option[Boolean],
  hash: Option[String])

case class ExtractResult(
  id: Int,
  tps: Int,
  photo: String,
  response: String,
  responseCode: Int,
  digitArea: String,
  config: String,
  tpsArea: String)

case class PresidentialResult(
  id: Int,
  tps: Int,
  photo: String,
  response: String,
  responseCode: Int,
  pas1: Int,
  pas2: Int,
  jumlahCalon: Int,
  calonConfidence: Double,
  jumlahSah: Int,
  tidakSah: Int,
  jumlahSeluruh: Int,
  jumlahConfidence: Double)

object ResultsTables extends SlickValueEnumSupport {
  val profile = slick.jdbc.SQLiteProfile

  class AlignResults(tag: Tag) extends Table[AlignResult](tag, "align_results") {
    def id = column[Int]("kelurahan")
    def tps = column[Int]("tps")
    def response = column[String]("response", O.SqlType("TEXT"))
    def responseCode = column[Int]("response_code")
    def photo = column[String]("photo", O.PrimaryKey)
    def photoSize = column[Int]("photo_size")
    def alignQuality = column[Int]("align_quality")
    def config = column[String]("config")
    def alignedUrl = column[Option[String]]("aligned_url")
    def extracted = column[Option[Boolean]]("extracted")
    def hash = column[Option[String]]("hash")

    override def * =
      (
        id,
        tps,
        response,
        responseCode,
        photo,
        photoSize,
        alignQuality,
        config,
        alignedUrl,
        extracted,
        hash) <> (AlignResult.tupled, AlignResult.unapply)
  }

  val alignResultsQuery = TableQuery[AlignResults]

  class ExtractResults(tag: Tag) extends Table[ExtractResult](tag, "extract_results") {
    def id = column[Int]("kelurahan")
    def tps = column[Int]("tps")
    def photo = column[String]("photo", O.PrimaryKey)
    def response = column[String]("response", O.SqlType("TEXT"))
    def responseCode = column[Int]("response_code")

    def digitArea = column[String]("digit_area")
    def config = column[String]("config")
    def tpsArea = column[String]("tps_area")

    override def * =
      (id, tps, photo, response, responseCode, digitArea, config, tpsArea) <> (ExtractResult.tupled, ExtractResult.unapply)
  }

  val extractResultsQuery = TableQuery[ExtractResults]

  class PresidentialResults(tag: Tag)
    extends Table[PresidentialResult](tag, "presidential_results") {
    def id = column[Int]("kelurahan")
    def tps = column[Int]("tps")
    def photo = column[String]("photo", O.PrimaryKey)

    def response = column[String]("response")
    def responseCode = column[Int]("response_code")

    def pas1 = column[Int]("pas1")
    def pas2 = column[Int]("pas2")
    def jumlahCalon = column[Int]("jumlah_calon")
    def calonConfidence = column[Double]("calon_conf")

    def jumlahSah = column[Int]("jumlah_sah")
    def tidakSah = column[Int]("tidak_sah")
    def jumlahSeluruh = column[Int]("jumlah_seluruh")
    def jumlahConfidence = column[Double]("jumlah_conf")

    override def * =
      (
        id,
        tps,
        photo,
        response,
        responseCode,
        pas1,
        pas2,
        jumlahCalon,
        calonConfidence,
        jumlahSah,
        tidakSah,
        jumlahSeluruh,
        jumlahConfidence) <>
        (PresidentialResult.tupled, PresidentialResult.unapply)
  }

  val presidentialResultsQuery = TableQuery[PresidentialResults]

  def upsertAlign(results: Seq[AlignResult]): Seq[FixedSqlAction[Int, NoStream, Effect.Write]] = {
    results.map(alignResultsQuery.insertOrUpdate)
  }

  def upsertExtract(
    results: Seq[ExtractResult]): Seq[FixedSqlAction[Int, NoStream, Effect.Write]] = {
    results.map(extractResultsQuery.insertOrUpdate)
  }

  def upsertPresidential(
    results: Seq[PresidentialResult]): Seq[FixedSqlAction[Int, NoStream, Effect.Write]] = {
    results.map(presidentialResultsQuery.insertOrUpdate)
  }
}
