package id.kawalc1.services

import akka.NotUsed
import akka.stream.Materializer
import akka.stream.scaladsl.Source

import scala.concurrent.Future

object FutureHelper {

  def sequence[A: Manifest, B](items: Seq[A], func: A => Future[B], parallelism: Int)(
    implicit
    mat: Materializer): Future[Seq[B]] = {
    val futures: Source[B, NotUsed] =
      Source[A](items.toList).mapAsync(parallelism)(x => func(x))

    futures.runFold(Seq.empty[B])(_ :+ _)
  }

}
