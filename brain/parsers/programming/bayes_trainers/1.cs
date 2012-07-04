/**
 * Parser for MARC records
 *
 * This project is based on the File_MARC package
 * (http://pear.php.net/package/File_MARC) by Dan Scott , which was based on PHP
 */


using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Collections;
using System.IO;

namespace MARC
{
    /// <summary>
    /// This is a wrapper for FileMARC that allows for reading large files without loading the entire file into memory.
    /// </summary>
    public class FileMARCReader : IEnumerable, IDisposable
    {
        //Member Variables and Properties
        #region Member Variables and Properties

        private string filename = null;
        private FileStream reader = null;

        #endregion

        //Constructors
        #region Constructors

        public FileMARCReader(string filename)
        {
            this.filename = filename;
            reader = new FileStream(this.filename, FileMode.Open, FileAccess.Read, FileShare.Read);
        }

        #endregion

        //Interface functions
        #region IEnumerator Members

        /// <summary>
        /// Gets the enumerator.
        /// </summary>
        /// <returns></returns>
        public IEnumerator GetEnumerator()
        {
            int bufferSize = 10 * 1024 * 1024;
            byte[] ByteArray = new byte[bufferSize + 1];
            while (reader.Position < reader.Length)
            {
                int DelPosition, RealReadSize;
                do
                {
                    RealReadSize = reader.Read(ByteArray, 0, bufferSize);

                    if (RealReadSize != bufferSize)
                        Array.Resize(ref ByteArray, RealReadSize + 1);

                    DelPosition = Array.LastIndexOf(ByteArray, Convert.ToByte(FileMARC.END_OF_RECORD)) + 1;

                    if (DelPosition == 0 & RealReadSize == bufferSize)
                    {
                        bufferSize *= 2;
                        ByteArray = new byte[bufferSize + 1];
                    }
                } while (DelPosition == 0 & RealReadSize == bufferSize);

                reader.Position = reader.Position - (RealReadSize - DelPosition);

                FileMARC marc = new FileMARC(Encoding.GetEncoding(1251).GetString(ByteArray, 0, DelPosition));
                foreach (Record marcRecord in marc)
                {
                    yield return marcRecord;
                }
            }
        }

        #endregion

        #region IDisposable Members

        public void Dispose()
        {
            reader.Dispose();
        }

        #endregion
    }
}