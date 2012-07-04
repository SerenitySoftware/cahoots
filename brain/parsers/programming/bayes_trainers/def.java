/*
 * Java CSV is a stream based library for reading and writing
 * CSV and other delimited data.
 */
package com.csvreader;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.BufferedWriter;
import java.io.Writer;
import java.nio.charset.Charset;

/**
 * A stream based writer for writing delimited text data to a file or a stream.
 */
public class CsvWriter {
    private Writer outputStream = null;
    
    private String fileName = null;

    private boolean firstColumn = true;

    private boolean useCustomRecordDelimiter = false;

    private Charset charset = null;

    // this holds all the values for switches that the user is allowed to set
    private UserSettings userSettings = new UserSettings();

    private boolean initialized = false;

    private boolean closed = false;
    
    private String systemRecordDelimiter = System.getProperty("line.separator");

    /**
     * Double up the text qualifier to represent an occurrence of the text
     * qualifier.
     */
    public static final int ESCAPE_MODE_DOUBLED = 1;

    /**
     * Use a backslash character before the text qualifier to represent an
     * occurrence of the text qualifier.
     */
    public static final int ESCAPE_MODE_BACKSLASH = 2;

    /**
     * Creates a {@link com.csvreader.CsvWriter CsvWriter} object using a file
     * as the data destination.
     * 
     * @param fileName
     *            The path to the file to output the data.
     * @param delimiter
     *            The character to use as the column delimiter.
     * @param charset
     *            The {@link java.nio.charset.Charset Charset} to use while
     *            writing the data.
     */
    public CsvWriter(String fileName, char delimiter, Charset charset) {
        if (fileName == null) {
            throw new IllegalArgumentException("Parameter fileName can not be null.");
        }

        if (charset == null) {
            throw new IllegalArgumentException("Parameter charset can not be null.");
        }

        this.fileName = fileName;
        userSettings.Delimiter = delimiter;
        this.charset = charset;
    }

    /**
     * Creates a {@link com.csvreader.CsvWriter CsvWriter} object using a file
     * as the data destination.&nbsp;Uses a comma as the column delimiter and
     * ISO-8859-1 as the {@link java.nio.charset.Charset Charset}.
     * 
     * @param fileName
     *            The path to the file to output the data.
     */
    public CsvWriter(String fileName) {
        this(fileName, Letters.COMMA, Charset.forName("ISO-8859-1"));
    }

    /**
     * Creates a {@link com.csvreader.CsvWriter CsvWriter} object using a Writer
     * to write data to.
     * 
     * @param outputStream
     *            The stream to write the column delimited data to.
     * @param delimiter
     *            The character to use as the column delimiter.
     */
    public CsvWriter(Writer outputStream, char delimiter) {
        if (outputStream == null) {
            throw new IllegalArgumentException("Parameter outputStream can not be null.");
        }

        this.outputStream = outputStream;
        userSettings.Delimiter = delimiter;
        initialized = true;
    }

    /**
     * Creates a {@link com.csvreader.CsvWriter CsvWriter} object using an
     * OutputStream to write data to.
     * 
     * @param outputStream
     *            The stream to write the column delimited data to.
     * @param delimiter
     *            The character to use as the column delimiter.
     * @param charset
     *            The {@link java.nio.charset.Charset Charset} to use while
     *            writing the data.
     */
    public CsvWriter(OutputStream outputStream, char delimiter, Charset charset) {
        this(new OutputStreamWriter(outputStream, charset), delimiter);
    }

    /**
     * Gets the character being used as the column delimiter.
     * 
     * @return The character being used as the column delimiter.
     */
    public char getDelimiter() {
        return userSettings.Delimiter;
    }

    /**
     * Sets the character to use as the column delimiter.
     * 
     * @param delimiter
     *            The character to use as the column delimiter.
     */
    public void setDelimiter(char delimiter) {
        userSettings.Delimiter = delimiter;
    }

    public char getRecordDelimiter() {
        return userSettings.RecordDelimiter;
    }

    /**
     * Sets the character to use as the record delimiter.
     * 
     * @param recordDelimiter
     *            The character to use as the record delimiter. Default is
     *            combination of standard end of line characters for Windows,
     *            Unix, or Mac.
     */
    public void setRecordDelimiter(char recordDelimiter) {
        useCustomRecordDelimiter = true;
        userSettings.RecordDelimiter = recordDelimiter;
    }

    /**
     * Gets the character to use as a text qualifier in the data.
     * 
     * @return The character to use as a text qualifier in the data.
     */
    public char getTextQualifier() {
        return userSettings.TextQualifier;
    }

    /**
     * Sets the character to use as a text qualifier in the data.
     * 
     * @param textQualifier
     *            The character to use as a text qualifier in the data.
     */
    public void setTextQualifier(char textQualifier) {
        userSettings.TextQualifier = textQualifier;
    }

    /**
     * Whether text qualifiers will be used while writing data or not.
     * 
     * @return Whether text qualifiers will be used while writing data or not.
     */
    public boolean getUseTextQualifier() {
        return userSettings.UseTextQualifier;
    }

    /**
     * Sets whether text qualifiers will be used while writing data or not.
     * 
     * @param useTextQualifier
     *            Whether to use a text qualifier while writing data or not.
     */
    public void setUseTextQualifier(boolean useTextQualifier) {
        userSettings.UseTextQualifier = useTextQualifier;
    }

    public int getEscapeMode() {
        return userSettings.EscapeMode;
    }

    public void setEscapeMode(int escapeMode) {
        userSettings.EscapeMode = escapeMode;
    }

    public void setComment(char comment) {
        userSettings.Comment = comment;
    }

    public char getComment() {
        return userSettings.Comment;
    }

    /**
     * Whether fields will be surrounded by the text qualifier even if the
     * qualifier is not necessarily needed to escape this field.
     * 
     * @return Whether fields will be forced to be qualified or not.
     */
    public boolean getForceQualifier() {
        return userSettings.ForceQualifier;
    }

    /**
     * Use this to force all fields to be surrounded by the text qualifier even
     * if the qualifier is not necessarily needed to escape this field. Default
     * is false.
     * 
     * @param forceQualifier
     *            Whether to force the fields to be qualified or not.
     */
    public void setForceQualifier(boolean forceQualifier) {
        userSettings.ForceQualifier = forceQualifier;
    }

    /**
     * Writes another column of data to this record.
     * 
     * @param content
     *            The data for the new column.
     * @param preserveSpaces
     *            Whether to preserve leading and trailing whitespace in this
     *            column of data.
     * @exception IOException
     *                Thrown if an error occurs while writing data to the
     *                destination stream.
     */
    public void write(String content, boolean preserveSpaces)
            throws IOException {
        checkClosed();

        checkInit();

        if (content == null) {
            content = "";
        }

        if (!firstColumn) {
            outputStream.write(userSettings.Delimiter);
        }

        boolean textQualify = userSettings.ForceQualifier;

        if (!preserveSpaces && content.length() > 0) {
            content = content.trim();
        }

        if (!textQualify
                && userSettings.UseTextQualifier
                && (content.indexOf(userSettings.TextQualifier) > -1
                        || content.indexOf(userSettings.Delimiter) > -1
                        || (!useCustomRecordDelimiter && (content
                                .indexOf(Letters.LF) > -1 || content
                                .indexOf(Letters.CR) > -1))
                        || (useCustomRecordDelimiter && content
                                .indexOf(userSettings.RecordDelimiter) > -1)
                        || (firstColumn && content.length() > 0 && content
                                .charAt(0) == userSettings.Comment) ||
                // check for empty first column, which if on its own line must
                // be qualified or the line will be skipped
                (firstColumn && content.length() == 0))) {
            textQualify = true;
        }

        if (userSettings.UseTextQualifier && !textQualify
                && content.length() > 0 && preserveSpaces) {
            char firstLetter = content.charAt(0);

            if (firstLetter == Letters.SPACE || firstLetter == Letters.TAB) {
                textQualify = true;
            }

            if (!textQualify && content.length() > 1) {
                char lastLetter = content.charAt(content.length() - 1);

                if (lastLetter == Letters.SPACE || lastLetter == Letters.TAB) {
                    textQualify = true;
                }
            }
        }

        if (textQualify) {
            outputStream.write(userSettings.TextQualifier);

            if (userSettings.EscapeMode == ESCAPE_MODE_BACKSLASH) {
                content = replace(content, "" + Letters.BACKSLASH, ""
                        + Letters.BACKSLASH + Letters.BACKSLASH);
                content = replace(content, "" + userSettings.TextQualifier, ""
                        + Letters.BACKSLASH + userSettings.TextQualifier);
            } else {
                content = replace(content, "" + userSettings.TextQualifier, ""
                        + userSettings.TextQualifier
                        + userSettings.TextQualifier);
            }
        } else if (userSettings.EscapeMode == ESCAPE_MODE_BACKSLASH) {
            content = replace(content, "" + Letters.BACKSLASH, ""
                    + Letters.BACKSLASH + Letters.BACKSLASH);
            content = replace(content, "" + userSettings.Delimiter, ""
                    + Letters.BACKSLASH + userSettings.Delimiter);

            if (useCustomRecordDelimiter) {
                content = replace(content, "" + userSettings.RecordDelimiter,
                        "" + Letters.BACKSLASH + userSettings.RecordDelimiter);
            } else {
                content = replace(content, "" + Letters.CR, ""
                        + Letters.BACKSLASH + Letters.CR);
                content = replace(content, "" + Letters.LF, ""
                        + Letters.BACKSLASH + Letters.LF);
            }

            if (firstColumn && content.length() > 0
                    && content.charAt(0) == userSettings.Comment) {
                if (content.length() > 1) {
                    content = "" + Letters.BACKSLASH + userSettings.Comment
                            + content.substring(1);
                } else {
                    content = "" + Letters.BACKSLASH + userSettings.Comment;
                }
            }
        }

        outputStream.write(content);

        if (textQualify) {
            outputStream.write(userSettings.TextQualifier);
        }

        firstColumn = false;
    }

    /**
     * Writes another column of data to this record.&nbsp;Does not preserve
     * leading and trailing whitespace in this column of data.
     * 
     * @param content
     *            The data for the new column.
     * @exception IOException
     *                Thrown if an error occurs while writing data to the
     *                destination stream.
     */
    public void write(String content) throws IOException {
        write(content, false);
    }

    public void writeComment(String commentText) throws IOException {
        checkClosed();

        checkInit();

        outputStream.write(userSettings.Comment);

        outputStream.write(commentText);

        if (useCustomRecordDelimiter) {
            outputStream.write(userSettings.RecordDelimiter);
        } else {
            outputStream.write(systemRecordDelimiter);
        }
        
        firstColumn = true;
    }

    /**
     * Writes a new record using the passed in array of values.
     * 
     * @param values
     *            Values to be written.
     * 
     * @param preserveSpaces
     *            Whether to preserver leading and trailing spaces in columns
     *            while writing out to the record or not.
     * 
     * @throws IOException
     *             Thrown if an error occurs while writing data to the
     *             destination stream.
     */
    public void writeRecord(String[] values, boolean preserveSpaces)
            throws IOException {
        if (values != null && values.length > 0) {
            for (int i = 0; i < values.length; i++) {
                write(values[i], preserveSpaces);
            }

            endRecord();
        }
    }

    /**
     * Writes a new record using the passed in array of values.
     * 
     * @param values
     *            Values to be written.
     * 
     * @throws IOException
     *             Thrown if an error occurs while writing data to the
     *             destination stream.
     */
    public void writeRecord(String[] values) throws IOException {
        writeRecord(values, false);
    }

    /**
     * Ends the current record by sending the record delimiter.
     * 
     * @exception IOException
     *                Thrown if an error occurs while writing data to the
     *                destination stream.
     */
    public void endRecord() throws IOException {
        checkClosed();

        checkInit();

        if (useCustomRecordDelimiter) {
            outputStream.write(userSettings.RecordDelimiter);
        } else {
            outputStream.write(systemRecordDelimiter);
        }

        firstColumn = true;
    }

    /**
     * 
     */
    private void checkInit() throws IOException {
        if (!initialized) {
            if (fileName != null) {
                outputStream = new BufferedWriter(new OutputStreamWriter(
                        new FileOutputStream(fileName), charset));
            }

            initialized = true;
        }
    }

    /**
     * Clears all buffers for the current writer and causes any buffered data to
     * be written to the underlying device.
     * @exception IOException
     *                Thrown if an error occurs while writing data to the
     *                destination stream. 
     */
    public void flush() throws IOException {
        outputStream.flush();
    }

    /**
     * Closes and releases all related resources.
     */
    public void close() {
        if (!closed) {
            close(true);

            closed = true;
        }
    }

    /**
     * 
     */
    private void close(boolean closing) {
        if (!closed) {
            if (closing) {
                charset = null;
            }

            try {
                if (initialized) {
                    outputStream.close();
                }
            } catch (Exception e) {
                // just eat the exception
            }

            outputStream = null;

            closed = true;
        }
    }

    /**
     * 
     */
    private void checkClosed() throws IOException {
        if (closed) {
            throw new IOException(
            "This instance of the CsvWriter class has already been closed.");
        }
    }

    /**
     * 
     */
    protected void finalize() {
        close(false);
    }

    private class Letters {
        public static final char LF = '\n';

        public static final char CR = '\r';

        public static final char QUOTE = '"';

        public static final char COMMA = ',';

        public static final char SPACE = ' ';

        public static final char TAB = '\t';

        public static final char POUND = '#';

        public static final char BACKSLASH = '\\';

        public static final char NULL = '\0';
    }

    private class UserSettings {
        // having these as publicly accessible members will prevent
        // the overhead of the method call that exists on properties
        public char TextQualifier;

        public boolean UseTextQualifier;

        public char Delimiter;

        public char RecordDelimiter;

        public char Comment;

        public int EscapeMode;

        public boolean ForceQualifier;

        public UserSettings() {
            TextQualifier = Letters.QUOTE;
            UseTextQualifier = true;
            Delimiter = Letters.COMMA;
            RecordDelimiter = Letters.NULL;
            Comment = Letters.POUND;
            EscapeMode = ESCAPE_MODE_DOUBLED;
            ForceQualifier = false;
        }
    }

    public static String replace(String original, String pattern, String replace) {
        final int len = pattern.length();
        int found = original.indexOf(pattern);

        if (found > -1) {
            StringBuffer sb = new StringBuffer();
            int start = 0;

            while (found != -1) {
                sb.append(original.substring(start, found));
                sb.append(replace);
                start = found + len;
                found = original.indexOf(pattern, start);
            }

            sb.append(original.substring(start));

            return sb.toString();
        } else {
            return original;
        }
    }
}

package net.sourceforge.javaocr;

/**
 * slices image into pieces. utilises iterator pattern, concrete implementations are provided for
 * horizontal and vertical slicing
 */
public interface ImageSlicer {
    /**
     * start horizontal slicing iteration from certain position  empty row means new image
     *
     * @param fromY starting Y
     */
    public ImageSlicer slice(int fromY);

    /**
     * start horizontal slicing with defined tolerance
     *
     * @param fromY     starting position
     * @param tolerance amount of empty rows allowed inside consecutive image
     */
    public ImageSlicer slice(int fromY, int tolerance);


    /**
     * whether next slice is available
     *
     * @return availability of next slice
     */
    boolean hasNext();


    /**
     * retrieve next slice and advance
     *
     * @return next image slice
     */
    Image next();
}

/*------------------------------------------------------------------------------
Name:      CSVReader.java
Project:   jutils.org
Comment:   Reads CSV (Comma Separated Value) files
Version:   $Id: CSVReader.java,v 1.1 2004/04/07 07:40:45 laurent Exp $
Author:    Roedy Green roedy@mindprod.com, Heinrich Goetzger goetzger@gmx.net
------------------------------------------------------------------------------*/
package org.jutils.csv;

import java.util.Vector;
import java.io.BufferedReader;
import java.io.EOFException;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;

/**
 * Reads CSV (Comma Separated Value) files.
 *
 * This format is mostly used my Microsoft Word and Excel.
 * Fields are separated by commas, and enclosed in
 * quotes if they contain commas or quotes.
 * Embedded quotes are doubled.
 * Embedded spaces do not normally require surrounding quotes.
 * The last field on the line is not followed by a comma.
 * Null fields are represented by two commas in a row.
 * We ignore leading and trailing spaces on fields, even inside quotes.
 *
 * @author copyright (c) 2002 Roedy Green  Canadian Mind Products
 * Roedy posted this code on Newsgroups:comp.lang.java.programmer on 27th March 2002.
 *
 * Heinrich added some stuff like comment ability and linewise working.
 *
 */

public class CSVReader {
   /**
    * Constructor
    *
    * @param r     input Reader source of CSV Fields to read.
    * @param separator
    *               field separator character, usually ',' in North America,
    *               ';' in Europe and sometimes '\t' for tab.
    */
   public CSVReader (Reader r, char separator) {
      /* convert Reader to BufferedReader if necessary */
      if ( r instanceof BufferedReader ) {
         this.r = (BufferedReader) r;
      } else {
         this.r = new BufferedReader(r);
      }
      this.separator = separator;
   } // end of CSVReader

   /**
    * Constructor with default field separator ','.
    *
    * @param r     input Reader source of CSV Fields to read.
    */
   public CSVReader (Reader r) {
      /* convert Reader to BufferedReader if necessary */
      if ( r instanceof BufferedReader ) {
         this.r = (BufferedReader) r;
      } else {
         this.r = new BufferedReader(r);
      }
      this.separator = ',';
   } // end of CSVReader

   private static final boolean debugging = true;

   /**
    * Reader source of the CSV fields to be read.
    */
   private BufferedReader r;

   /*
   * field separator character, usually ',' in North America,
   * ';' in Europe and sometimes '\t' for tab.
   */
   private char separator;

   /**
    * category of end of line char.
    */
   private static final int EOL = 0;

   /**
    * category of ordinary character
    */
   private static final int ORDINARY = 1;

   /**
    * categotory of the quote mark "
    */
   private static final int QUOTE = 2;

   /**
    * category of the separator, e.g. comma, semicolon
    * or tab.
    */
   private static final int SEPARATOR = 3;

   /**
    * category of characters treated as white space.
    */
   private static final int WHITESPACE = 4;

   /**
    * categorise a character for the finite state machine.
    *
    * @param c      the character to categorise
    * @return integer representing the character's category.
    */
   private int categorise ( char c ) {
      switch ( c ) {
         case ' ':
         case '\r':
         case 0xff:
            return WHITESPACE;
//         case ';':
//         case '!':
         case '#':
            //return EOL;
         case '\n':
            return EOL; /* artificially applied to end of line */
         case '\"':
            return QUOTE;
         default:
            if (c == separator) {
               /* dynamically determined so can't use as case label */
               return SEPARATOR;
            } else if ( '!' <= c && c <= '~' ) {
               /* do our tests in crafted order, hoping for an early return */
               return ORDINARY;
            } else if ( 0x00 <= c && c <= 0x20 ) {
               return WHITESPACE;
            } else if ( Character.isWhitespace(c) ) {
               return WHITESPACE;
            } else {
               return ORDINARY;
            }
      } // end of switch
   } // end of categorise


   /**
    * parser: We are in blanks before the field.
    */
   private static final int SEEKINGSTART = 0;

   /**
    * parser: We are in the middle of an ordinary field.
    */
   private static final int INPLAIN = 1;

   /**
    * parser: e are in middle of field surrounded in quotes.
    */
   private static final int INQUOTED = 2;

   /**
    * parser: We have just hit a quote, might be doubled
    * or might be last one.
    */
   private static final int AFTERENDQUOTE = 3;

   /**
   * parser: We are in blanks after the field looking for the separator
   */
   private static final int SKIPPINGTAIL = 4;

   /**
    * state of the parser's finite state automaton.
    */

   /**
    * The line we are parsing.
    * null means none read yet.
    * Line contains unprocessed chars. Processed ones are removed.
    */
   private String line = null;

   /**
    * How many lines we have read so far.
    * Used in error messages.
    */
   private int lineCount = 0;

   public String[] getLine() {
      Vector lineArray = new Vector();
      String token = null;
      String returnArray [] = null;

      // reading values from line until null comes

      try {
         while (lineArray.size() == 0) {
            while ( (token = get() ) != null ) {
               lineArray.add(token);
            } // end of while
         } // end of while
      } catch (EOFException e) {
         return null;
      } catch (IOException e) {
      }

      returnArray = new String[lineArray.size()];

      for(int ii=0; ii < lineArray.size(); ii++) {
         returnArray[ii] = lineArray.elementAt(ii).toString();
      } // end of for

      return returnArray;
   }

   /**
    * Read one field from the CSV file
    *
    * @return String value, even if the field is numeric.  Surrounded
    *         and embedded double quotes are stripped.
    *         possibly "".  null means end of line.
    *
    * @exception EOFException
    *                   at end of file after all the fields have
    *                   been read.
    *
    * @exception IOException
    *                   Some problem reading the file, possibly malformed data.
    */
   private String get() throws EOFException, IOException {
      StringBuffer field = new StringBuffer(50);
      /* we implement the parser as a finite state automaton with five states. */
      readLine();

      int state = SEEKINGSTART; /* start seeking, even if partway through a line */
      /* don't need to maintain state between fields. */

      /* loop for each char in the line to find a field */
      /* guaranteed to leave early by hitting EOL */
      for ( int i=0; i<line.length(); i++ ) {
         char c = line.charAt(i);
         int category = categorise(c);
         switch ( state ) {
            case SEEKINGSTART: {
               /* in blanks before field */
               switch ( category ) {
                  case WHITESPACE:
                     /* ignore */
                     break;
                  case QUOTE:
                     state = INQUOTED;
                     break;
                  case SEPARATOR:
                     /* end of empty field */
                     line = line.substring(i+1);
                     return "";
                  case EOL:
                     /* end of line */
                     line = null;
                     return null;
                  case ORDINARY:
                     field.append(c);
                     state = INPLAIN;
                     break;
               }
               break;
            } // end of SEEKINGSTART
            case INPLAIN: {
               /* in middle of ordinary field */
               switch ( category ) {
                  case QUOTE:
                     throw new IOException("Malformed CSV stream. Missing quote at start of field on line " + lineCount);
                  case SEPARATOR:
                     /* done */
                     line = line.substring(i+1);
                     return field.toString().trim();
                  case EOL:
                     line = line.substring(i); /* push EOL back */
                     return field.toString().trim();
                  case WHITESPACE:
                     field.append(' ');
                     break;
                  case ORDINARY:
                     field.append(c);
                     break;
               }
               break;
            } // end of INPLAIN
            case INQUOTED: {
               /* in middle of field surrounded in quotes */
               switch ( category ) {
                  case QUOTE:
                     state = AFTERENDQUOTE;
                     break;
                  case EOL:
                     throw new IOException ("Malformed CSV stream. Missing quote after field on line "+lineCount);
                  case WHITESPACE:
                     field.append(' ');
                     break;
                  case SEPARATOR:
                  case ORDINARY:
                     field.append(c);
                     break;
               }
                break;
            } // end of INQUOTED
            case AFTERENDQUOTE: {
               /* In situation like this "xxx" which may
                  turn out to be xxx""xxx" or "xxx",
                  We find out here. */
               switch ( category ) {
                     case QUOTE:
                        field.append(c);
                        state = INQUOTED;
                        break;
                     case SEPARATOR :
                        /* we are done.*/
                        line = line.substring(i+1);
                        return field.toString().trim();
                     case EOL:
                        line = line.substring(i); /* push back eol */
                        return field.toString().trim();
                     case WHITESPACE:
                        /* ignore trailing spaces up to separator */
                        state = SKIPPINGTAIL;
                        break;
                     case ORDINARY:
                        throw new IOException("Malformed CSV stream, missing separator after field on line " + lineCount);
               }
               break;
            } // end of AFTERENDQUOTE
            case SKIPPINGTAIL: {
               /* in spaces after field seeking separator */
               switch ( category ) {
                  case SEPARATOR :
                     /* we are done.*/
                     line = line.substring(i+1);
                     return field.toString().trim();
                  case EOL:
                     line = line.substring(i); /* push back eol */
                     return field.toString().trim();
                  case WHITESPACE:
                     /* ignore trailing spaces up to separator */
                     break;
                  case QUOTE:
                  case ORDINARY:
                     throw new IOException("Malformed CSV stream, missing separator after field on line " + lineCount);
               } // end of switch
               break;
            } // end of SKIPPINGTAIL
         } // end switch(state)
      } // end for
      throw new IOException("Program logic bug. Should not reach here. Processing line " + lineCount);
   } // end get

   /**
    * Make sure a line is available for parsing.
    * Does nothing if there already is one.
    *
    * @exception EOFException
    */
   private void readLine() throws EOFException, IOException {
      if ( line == null ) {
         line = r.readLine();  /* this strips platform specific line ending */
         if ( line == null ) {
                /* null means EOF, yet another inconsistent Java convention. */
            throw new EOFException();
         } else {
            line += '\n'; /* apply standard line end for parser to find */
            lineCount++;
         }
      }
   } // end of readLine


   /**
    * Skip over fields you don't want to process.
    *
    * @param fields How many field you want to bypass reading.
    *               The newline counts as one field.
    * @exception EOFException
    *                   at end of file after all the fields have
    *                   been read.
    * @exception IOException
    *                   Some problem reading the file, possibly malformed data.
    */
   public void skip(int fields) throws EOFException, IOException {
      if ( fields <= 0 ) {
         return;
      }
      for ( int i=0; i<fields; i++ ) {
         // throw results away
         get();
      }
   } // end of skip

   /**
    * Skip over remaining fields on this line you don't want to process.
    *
    * @exception EOFException
    *                   at end of file after all the fields have
    *                   been read.
    * @exception IOException
    *                   Some problem reading the file, possibly malformed data.
    */
   public void skipToNextLine() throws EOFException, IOException {
      if ( line == null ) {
         readLine();
      }
      line = null;
   } // end of skipToNextLine

   /**
    * Close the Reader.
    */
   public void close() throws IOException {
      if ( r != null ) {
         r.close();
         r = null;
      }
   } // end of close

   /**
    * @param args  [0]: The name of the file.
    */
   private static void testSingleTokens(String[] args) {
      if ( debugging ) {
         try {
            // read test file
              CSVReader csv = new CSVReader(new FileReader(args[0]), ',');
           try {
               while ( true ) {
                  System.out.println(csv.get());
               }
            } catch ( EOFException  e ) {
                }
                csv.close();
         } catch ( IOException  e ) {
            e.printStackTrace();
            System.out.println(e.getMessage());
         }
      } // end if
   } // end of testSingleTokens

   /**
    * @param args  [0]: The name of the file.
    */
   private static void testLines(String[] args) {
      int lineCounter = 0;
      String loadLine[] = null;
      String DEL = ",";

      if ( debugging ) {
         try {
            // read test file
            CSVReader csv = new CSVReader(new FileReader(args[0]), ',');

            while( (loadLine = csv.getLine()) != null) {
               lineCounter++;
               StringBuffer logBuffer = new StringBuffer();
               String logLine;
               //log.debug("#" + lineCounter +" : '" + loadLine.length + "'");
               logBuffer.append(loadLine[0]); // write first token, then write DEL in loop and the whole rest.
               for(int i=1; i < loadLine.length; i++) {
                  logBuffer.append(DEL).append(loadLine[i]);
               }
               logLine = logBuffer.toString();
               logLine.substring(0, logLine.lastIndexOf(DEL));
               //logLine.delete(logLine.lastIndexOf(DEL), logLine.length()); // is supported since JDK 1.4
               //System.out.println("#" + lineCounter +" : '" + loadLine.length + "' " + logLine);
               System.out.println(logLine);
            } // end of while
                csv.close();
         } catch ( IOException  e ) {
            e.printStackTrace();
            System.out.println(e.getMessage());
         }
      } // end if
   } // end of testLines

   /**
    * Test driver
    *
    * @param args  [0]: The name of the file.
    */
   static public void main(String[] args) {
      //testSingleTokens(args);
      testLines(args);
   } // end main
} // end CSVReader

// end of file

/*
 * Copyright (c) 1999-2004 Sourceforge JACOB Project.
 * All rights reserved. Originator: Dan Adler (http://danadler.com).
 * Get more information about JACOB at http://sourceforge.net/projects/jacob-project
 */
package com.jacob.com;

/**
 * If you need to pass a COM Dispatch object between STA threads, you have to
 * marshall the interface. This class is used as follows: the STA that creates
 * the Dispatch object must construct an instance of this class. Another thread
 * can then call toDispatch() on that instance and get a Dispatch pointer which
 * has been marshalled. WARNING: You can only call toDispatch() once! If you
 * need to call it multiple times (or from multiple threads) you need to
 * construct a separate DispatchProxy instance for each such case!
 */
public class DispatchProxy extends JacobObject {
    /**
     * Comment for <code>m_pStream</code>
     */
    public long m_pStream;

    /**
     * Marshals the passed in dispatch into the stream
     * 
     * @param localDispatch
     */
    public DispatchProxy(Dispatch localDispatch) {
        MarshalIntoStream(localDispatch);
    }

    /**
     * 
     * @return Dispatch the dispatch retrieved from the stream
     */
    public Dispatch toDispatch() {
        return MarshalFromStream();
    }

    private native void MarshalIntoStream(Dispatch d);

    private native Dispatch MarshalFromStream();

    /**
     * now private so only this object can access was: call this to explicitly
     * release the com object before gc
     * 
     */
    private native void release();

    /*
     * (non-Javadoc)
     * 
     * @see java.lang.Object#finalize()
     */
    @Override
    public void finalize() {
        safeRelease();
    }

    /*
     * (non-Javadoc)
     * 
     * @see com.jacob.com.JacobObject#safeRelease()
     */
    @Override
    public void safeRelease() {
        super.safeRelease();
        if (m_pStream != 0) {
            release();
            m_pStream = 0;
        } else {
            // looks like a double release
            if (isDebugEnabled()) {
                debug(this.getClass().getName() + ":" + this.hashCode()
                        + " double release");
            }
        }
    }
}

/*
  Copyright (C) 2001-2003 Laurent Martelli <laurent@aopsys.com>

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as
  published by the Free Software Foundation; either version 2 of the
  License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA */

package org.objectweb.jac.util;

import java.util.Collection;
import java.util.List;
import java.io.File;
import java.util.Vector;
import java.util.Iterator;

/**
 * Various often used string functions
 */
public class Strings
{
   /**
    * Replace slashed characters ("\t" -> '\t',"\r" -> '\t',
    * "\n" -> '\n' ,"\f" -> '\f' , "\_" -> ' ') 
    */
   public static String unslashify (String str) {
      StringBuffer ret = new StringBuffer(str.length());
      int i=0;
      while(i<str.length()) {
         char c = str.charAt(i++);
         if (c == '\\') {
            c = str.charAt(i++);
            switch (c) {
               case 't': c='\t'; break;
               case 'r': c='\r'; break;
               case 'n': c='\n'; break;
               case 'f': c='\f'; break;
               case '_': c=' '; break;
            }
         } 
         ret.append(c);
      }
      return ret.toString();
   }

   /**
    * The reverse of unslashify. slashify(unslashify(str)).equals(str).
    */ 
   public static String slashify(String str) {
      StringBuffer ret = new StringBuffer(str.length());
      for(int i=0; i<str.length(); i++) {
         char c = str.charAt(i);
         switch (c) {
            case '\\': ret.append("\\\\"); break;
            case '\t': ret.append("\\t"); break;
            case '\r': ret.append("\\r"); break;
            case '\n': ret.append("\\n"); break;
            case '\f': ret.append("\\f"); break;
            case ' ': ret.append("\\_"); break;
            default: ret.append(c); break;
         }
      }
      return ret.toString();
   }

   /**
    * Split a string into an array
    * @param source string to split
    * @param separator the separator
    * @return an array of strings
    * @see #splitToList(String,String)
    */
   public static String[] split(String source, String separator) {
      return (String[])splitToList(source,separator).toArray(new String[0]);
   }

   /**
    * Split a string into a list of strings
    * @param source string to split
    * @param separator the separator
    * @return a list of strings
    * @see #split(String,String)
    */
   public static List splitToList(String source, String separator) {
      Vector tmp = new Vector();
      int startIndex =0;
      int index = 0;
      while ((index = source.indexOf(separator,startIndex))!=-1) {
         tmp.add(source.substring(startIndex,index));
         startIndex = index+separator.length();
      }
      if (source.length()>0 && startIndex<source.length())
         tmp.add(source.substring(startIndex));
      return tmp;
   }

   public static String join(Collection items, String separator) {
      StringBuffer result = new StringBuffer();
      Iterator it = items.iterator();
      while (it.hasNext()) {
         result.append(it.next().toString());
         if (it.hasNext())
            result.append(separator);
      }
      return result.toString();
   }

   public static String join(String[] items, String separator) {
      StringBuffer result = new StringBuffer();
      for (int i=0; i<items.length; i++) {
         if (i>0)
            result.append(separator);
         result.append(items[i]);
      }
      return result.toString();
   }

   /**
    * Split a list of paths separated by path.separator
    *
    * @return an array of path
    */
   public static String[] splitPath(String paths) {
      return Strings.split(paths,System.getProperty("path.separator"));
   }

   /**
    * Create a path string, using the appropriate path separator
    * @param paths a collection of File
    * @return the filenames of paths, separated by the appropriate path separator
    */
   public static String createPathString(Collection paths) {
      String separator = System.getProperty("path.separator");
      String pathString = null;
      Iterator it = paths.iterator();
      while (it.hasNext()) {
         File path = (File)it.next();
         if (pathString==null)
            pathString = path.toString();
         else
            pathString += separator+path.toString();
      }
      return pathString;
   }

   /**
    * Build a String representation of an object of the form
    * &lt;classname&gt;@&lt;hashcode&gt; 
    * @param o the object to stringify
    * @return a String representation of the object
    */
   public static String hex(Object o) {
      return o==null?"null":o.getClass().getName()+"@"+Integer.toHexString(o.hashCode());
   }
   
   /**
    * Build a String representation of a vector in the way as
    * Vector.toString(), but without brackets.  
    * @param vector the vector to stringify
    * @return a String representation of the vector
    */
   private static String toString(Vector vector) {
      if (vector.isEmpty()) 
         return "";
      String ls = vector.toString();
      return ls.substring(1, ls.length() - 1);
   }

   /**
    * Build a string with a given length and all the characters
    * equals.
    * @param c the character to fill the string with
    * @param length the length of the string
    * @return a string with the required length where
    * string.charAt(i)==c for all i between 0 and lenght-1.
    */
   public static String newString(char c, int length) {
      char[] array = new char[length];
      for (length--;length>=0;length--) {
         array[length] = c;
      }
      return new String(array);
   }

   /**
    * A useful method that replaces all the occurences of a string.
    *
    * @param orgString the original string
    * @param oldString the string to replace (if found) in the
    * original string
    * @param newString the string that replaces all the occurences of
    * old string
    * @return a new string with the occurences replaced 
    */
   public static String replace(String orgString, 
                                String oldString, String newString) {

      int pos = 0;
      boolean end = false;

      StringBuffer result = new StringBuffer(orgString.length()*2);

      int oldLen = oldString.length();
      while (!end) {
         int newpos = orgString.indexOf(oldString,pos);
         if (newpos != -1) {
            result.append(orgString.substring(pos, newpos));
            result.append(newString);
         } else {
            result.append(orgString.substring(pos));
            end = true;
         }
         pos = newpos + oldLen;
      }
      return result.toString();
   }

   /**
    * Replaces all occurences of some characters by a character
    * @param oldChars the characters that should be replaced
    * @param newChar the character by which to replace
    * @param s the string buffer whose's characters must be replaced
    */
   public static void replace(String oldChars, char newChar, StringBuffer s) {
      for (int i=0; i<s.length(); i++) {
         if (oldChars.indexOf(s.charAt(i))!=-1)
            s.setCharAt(i,newChar);
      }
   }

   /**
    * Replaces all occurences of some characters by a character
    * @param oldChars the characters that should be replaced
    * @param newChar the character by which to replace
    * @param s the string whose's characters must be replaced
    */
   public static String replace(String oldChars, char newChar, String s) {
      StringBuffer result = new StringBuffer(s);
      replace(oldChars,newChar,result);
      return result.toString();
   }

   /**
    * Delete occurences of characters from a StringBuffer
    * @param delChars the characters to delete
    * @param s the StringBuffer to remlove the characters from
    */
   public static void deleteChars(String delChars, StringBuffer s) {
      int length = s.length();
      int current = 0;
      for (int i=0; i<length; i++) {
         char c = s.charAt(i);
         if (delChars.indexOf(c)==-1) {
            s.setCharAt(current,c);
            current++;
         }
      }
      s.setLength(current);
   }

   public static String getShortClassName(Class cl) {
      String type = cl.getName();
      if (cl.isArray()) {
         type = cl.getComponentType().getName();
      }
      type = type.substring(type.lastIndexOf( '.' )+1);
      if (cl.isArray()) {
         type = type + "[]";
      }
      return type;
   }   

   public static String getShortClassName(String className) {
      return className.substring(className.lastIndexOf( '.' )+1);
   }

   public static String toUSAscii(String s) {
      StringBuffer result = new StringBuffer(s);
      toUSAscii(result);
      return result.toString();
   }

   /**
    * Lowers all characters of a StringBuffer
    */
   public static void toLowerCase(StringBuffer s) {
      for (int i=0; i<s.length(); i++) {
         s.setCharAt(i,Character.toLowerCase(s.charAt(i)));
      }
   }

   /**
    * Uppers all characters of a StringBuffer
    */
   public static void toUpperCase(StringBuffer s) {
      for (int i=0; i<s.length(); i++) {
         s.setCharAt(i,Character.toUpperCase(s.charAt(i)));
      }
   }

   /**
    * Replace accented chars with their non-accented value. For
    * instance, 'é' becomes 'e'.
    * @param s string to convert
    * @return converted string
    */
   public static void toUSAscii(StringBuffer s) {
      for (int i=s.length()-1; i>=0; i--) {
         switch (s.charAt(i)) {
            case 'é':
            case 'è':
            case 'ê':
            case 'ë':
               s.setCharAt(i, 'e');
               break;
            case 'É':
            case 'È':
            case 'Ê':
            case 'Ë':
               s.setCharAt(i, 'E');
               break;
            case 'ï':
            case 'î':
            case 'ì':
            case 'í':
               s.setCharAt(i, 'i');
               break;
            case 'Ï':
            case 'Î':
            case 'Ì':
            case 'Í':
               s.setCharAt(i, 'I');
               break;
            case 'à':
            case 'â':
            case 'ä':
            case 'ã':
            case 'å':
               s.setCharAt(i, 'a');
               break;
            case 'À':
            case 'Â':
            case 'Ä':
            case 'Ã':
            case 'Å':
               s.setCharAt(i, 'A');
               break;
            case 'ù':
            case 'ú':
            case 'ü':
            case 'û':
               s.setCharAt(i, 'u');
               break;
            case 'Ù':
            case 'Ú':
            case 'Ü':
            case 'Û':
               s.setCharAt(i, 'U');
               break;
            case 'ö':
            case 'ô':
            case 'ó':
            case 'ò':
            case 'õ':
               s.setCharAt(i, 'o');
               break;
            case 'Ö':
            case 'Ô':
            case 'Ó':
            case 'Ò':
            case 'Õ':
               s.setCharAt(i, 'O');
               break;
            case 'ç':
               s.setCharAt(i, 'c');
               break;
            case 'Ç':
               s.setCharAt(i, 'C');
               break;
            case 'ÿ':
            case 'ý':
               s.setCharAt(i, 'y');
               break;
            case 'Ý':
               s.setCharAt(i, 'Y');
               break;
            case 'ñ':
               s.setCharAt(i, 'n');
               break;
            case 'Ñ':
               s.setCharAt(i, 'N');
               break;
            default:
         }
      }
   }

   /**
    * Compares the USAscii representation of two strings in a case insensitive manner. 
    * @param a first string to compare
    * @param b second string to compare
    * @return true if a and b are equals
    */
   public static boolean equalsUSAsciiNoCase(String a, String b) {
      if (a==null)
         return b==null;
      else if (b==null)
         return a==null;
      else 
         return toUSAscii(a).toLowerCase().equals(toUSAscii(b).toLowerCase());
   }

   /**
    * Tells if a string is empty (is null, has a zero length, or
    * contains only whitespaces)
    * @param str string to test
    * @return true if str is null, str.length()==0 or str.trim().length()==0
    */
   public static boolean isEmpty(String str) {
      return str==null || str.length()==0 || str.trim().length()==0;
   }

   /**
    * Removes all whitespace and CR/LF characters at the beginning or
    * at the end of a string.
    * @param str the string to trim
    */
   public static String trimWSAndCRLF(String str) {
      if (str==null || str.length()==0)
         return str;

      // Trim at the beginning
      int start = 0;
      char c = str.charAt(start);
      while (Character.isWhitespace(c) || c=='\n' || c=='\r') {
         start++;
         if (start>=str.length())
            break;
         c = str.charAt(start);
      }

      // Trim at the end
      int end = str.length()-1;
      c = str.charAt(end);
      while (end>=start && (Character.isWhitespace(c) || c=='\n' || c=='\r')) {
         end--;
         c = str.charAt(end);
      }
      if (end<start)
         return "";
      else
         return str.substring(start,end+1);
   }
}

/********************************************************************
 * Copyright (c) 2007 Contributors. All rights reserved. 
 * This program and the accompanying materials are made available 
 * under the terms of the Eclipse Public License v1.0 
 * which accompanies this distribution and is available at 
 * http://eclipse.org/legal/epl-v10.html 
 *  
 * Contributors: IBM Corporation - initial API and implementation 
 *               Helen Hawkins   - initial version (bug 148190)
 *******************************************************************/
package org.aspectj.ajde.core.internal;

import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.StringTokenizer;

import org.aspectj.ajde.core.AjCompiler;
import org.aspectj.ajde.core.ICompilerConfiguration;
import org.aspectj.ajde.core.IOutputLocationManager;
import org.aspectj.ajdt.ajc.AjdtCommand;
import org.aspectj.ajdt.ajc.BuildArgParser;
import org.aspectj.ajdt.ajc.ConfigParser;
import org.aspectj.ajdt.internal.core.builder.AjBuildConfig;
import org.aspectj.ajdt.internal.core.builder.AjBuildManager;
import org.aspectj.ajdt.internal.core.builder.AjState;
import org.aspectj.ajdt.internal.core.builder.IncrementalStateManager;
import org.aspectj.asm.AsmManager;
import org.aspectj.bridge.AbortException;
import org.aspectj.bridge.CountingMessageHandler;
import org.aspectj.bridge.IMessage;
import org.aspectj.bridge.IMessageHandler;
import org.aspectj.bridge.ISourceLocation;
import org.aspectj.bridge.Message;
import org.aspectj.bridge.SourceLocation;
import org.aspectj.bridge.context.CompilationAndWeavingContext;
import org.aspectj.org.eclipse.jdt.internal.compiler.impl.CompilerOptions;
import org.aspectj.util.LangUtil;

/**
 * Build Manager which drives the build for a given AjCompiler. Tools call build on the AjCompiler which drives this.
 */
public class AjdeCoreBuildManager {

    private final AjCompiler compiler;
    private AjdeCoreBuildNotifierAdapter buildEventNotifier = null;
    private final AjBuildManager ajBuildManager;
    private final IMessageHandler msgHandlerAdapter;

    public AjdeCoreBuildManager(AjCompiler compiler) {
        this.compiler = compiler;
        this.msgHandlerAdapter = new AjdeCoreMessageHandlerAdapter(compiler.getMessageHandler());
        this.ajBuildManager = new AjBuildManager(msgHandlerAdapter);
        this.ajBuildManager.environmentSupportsIncrementalCompilation(true);

        // this static information needs to be set to ensure
        // incremental compilation works correctly
        IncrementalStateManager.recordIncrementalStates = true;
        IncrementalStateManager.debugIncrementalStates = false;
        AsmManager.attemptIncrementalModelRepairs = true;
    }

    public AjBuildManager getAjBuildManager() {
        return ajBuildManager;
    }

    /**
     * Execute a full or incremental build
     * 
     * @param fullBuild true if requesting a full build, false if requesting to try an incremental build
     */
    public void performBuild(boolean fullBuild) {

        // If an incremental build is requested, check that we can
        if (!fullBuild) {
            AjState existingState = IncrementalStateManager.retrieveStateFor(compiler.getId());
            if (existingState == null || existingState.getBuildConfig() == null
                    || ajBuildManager.getState().getBuildConfig() == null) {
                // No existing state so we must do a full build
                fullBuild = true;
            } else {
                AsmManager.setLastActiveStructureModel(existingState.getStructureModel());
                // AsmManager.getDefault().setRelationshipMap(existingState.getRelationshipMap());
                // AsmManager.getDefault().setHierarchy(existingState.getStructureModel());
            }
        }
        try {
            reportProgressBegin();

            // record the options passed to the compiler if INFO turned on
            if (!msgHandlerAdapter.isIgnoring(IMessage.INFO)) {
                handleMessage(new Message(getFormattedOptionsString(), IMessage.INFO, null, null));
            }

            CompilationAndWeavingContext.reset();

            if (fullBuild) { // FULL BUILD
                AjBuildConfig buildConfig = generateAjBuildConfig();
                if (buildConfig == null) {
                    return;
                }
                ajBuildManager.batchBuild(buildConfig, msgHandlerAdapter);
            } else { // INCREMENTAL BUILD
                // Only rebuild the config object if the configuration has changed
                AjBuildConfig buildConfig = null;
                ICompilerConfiguration compilerConfig = compiler.getCompilerConfiguration();
                int changes = compilerConfig.getConfigurationChanges();
                if (changes != ICompilerConfiguration.NO_CHANGES) {

                    // What configuration changes can we cope with? And besides just repairing the config object
                    // what does it mean for any existing state that we have?

                    buildConfig = generateAjBuildConfig();
                    if (buildConfig == null) {
                        return;
                    }
                } else {
                    buildConfig = ajBuildManager.getState().getBuildConfig();
                    buildConfig.setChanged(changes); // pass it through for the state to use it when making decisions
                    buildConfig.setModifiedFiles(compilerConfig.getProjectSourceFilesChanged());
                    buildConfig.setClasspathElementsWithModifiedContents(compilerConfig.getClasspathElementsWithModifiedContents());
                    compilerConfig.configurationRead();
                }
                ajBuildManager.incrementalBuild(buildConfig, msgHandlerAdapter);
            }
            IncrementalStateManager.recordSuccessfulBuild(compiler.getId(), ajBuildManager.getState());

        } catch (ConfigParser.ParseException pe) {
            handleMessage(new Message("Config file entry invalid, file: " + pe.getFile().getPath() + ", line number: "
                    + pe.getLine(), IMessage.WARNING, null, null));
        } catch (AbortException e) {
            final IMessage message = e.getIMessage();
            if (message == null) {
                handleMessage(new Message(LangUtil.unqualifiedClassName(e) + " thrown: " + e.getMessage(), IMessage.ERROR, e, null));
            } else {
                handleMessage(new Message(message.getMessage() + "\n" + CompilationAndWeavingContext.getCurrentContext(),
                        IMessage.ERROR, e, null));
            }
        } catch (Throwable t) {
            handleMessage(new Message("Compile error: " + LangUtil.unqualifiedClassName(t) + " thrown: " + "" + t.getMessage(),
                    IMessage.ABORT, t, null));
        } finally {
            compiler.getBuildProgressMonitor().finish(ajBuildManager.wasFullBuild());
        }
    }

    /**
     * Starts the various notifiers which are interested in the build progress
     */
    private void reportProgressBegin() {
        compiler.getBuildProgressMonitor().begin();
        buildEventNotifier = new AjdeCoreBuildNotifierAdapter(compiler.getBuildProgressMonitor());
        ajBuildManager.setProgressListener(buildEventNotifier);
    }

    private String getFormattedOptionsString() {
        ICompilerConfiguration compilerConfig = compiler.getCompilerConfiguration();
        return "Building with settings: " + "\n-> output paths: "
                + formatCollection(compilerConfig.getOutputLocationManager().getAllOutputLocations()) + "\n-> classpath: "
                + compilerConfig.getClasspath() + "\n-> -inpath " + formatCollection(compilerConfig.getInpath()) + "\n-> -outjar "
                + formatOptionalString(compilerConfig.getOutJar()) + "\n-> -aspectpath "
                + formatCollection(compilerConfig.getAspectPath()) + "\n-> -sourcePathResources "
                + formatMap(compilerConfig.getSourcePathResources()) + "\n-> non-standard options: "
                + compilerConfig.getNonStandardOptions() + "\n-> javaoptions:" + formatMap(compilerConfig.getJavaOptionsMap());
    }

    private String formatCollection(Collection<?> options) {
        if (options == null) {
            return "<default>";
        }
        if (options.isEmpty()) {
            return "none";
        }

        StringBuffer formattedOptions = new StringBuffer();
        Iterator<?> it = options.iterator();
        while (it.hasNext()) {
            String o = it.next().toString();
            if (formattedOptions.length() > 0) {
                formattedOptions.append(", ");
            }
            formattedOptions.append(o);
        }
        return formattedOptions.toString();
    }

    private String formatMap(Map options) {
        if (options == null) {
            return "<default>";
        }
        if (options.isEmpty()) {
            return "none";
        }

        return options.toString();
    }

    private String formatOptionalString(String s) {
        if (s == null) {
            return "";
        } else {
            return s;
        }
    }

    /**
     * Generate a new AjBuildConfig from the compiler configuration associated with this AjdeCoreBuildManager or from a
     * configuration file.
     * 
     * @return null if invalid configuration, corresponding AjBuildConfig otherwise
     */
    public AjBuildConfig generateAjBuildConfig() {
        File configFile = new File(compiler.getId());
        ICompilerConfiguration compilerConfig = compiler.getCompilerConfiguration();
        CountingMessageHandler handler = CountingMessageHandler.makeCountingMessageHandler(msgHandlerAdapter);

        String[] args = null;
        // Retrieve the set of files from either an arg file (@filename) or the compiler configuration
        if (configFile.exists() && configFile.isFile()) {
            args = new String[] { "@" + configFile.getAbsolutePath() };
        } else {
            List<String> l = compilerConfig.getProjectSourceFiles();
            if (l == null) {
                return null;
            }
            List<String> xmlfiles = compilerConfig.getProjectXmlConfigFiles();
            if (xmlfiles != null && !xmlfiles.isEmpty()) {
                args = new String[l.size() + xmlfiles.size() + 1];
                // TODO speedup
                int p = 0;
                for (int i = 0; i < l.size(); i++) {
                    args[p++] = (String) l.get(i);
                }
                for (int i = 0; i < xmlfiles.size(); i++) {
                    args[p++] = (String) xmlfiles.get(i);
                }
                args[p++] = "-xmlConfigured";
            } else {
                args = (String[]) l.toArray(new String[l.size()]);
            }
        }

        BuildArgParser parser = new BuildArgParser(handler);

        AjBuildConfig config = new AjBuildConfig();

        parser.populateBuildConfig(config, args, false, configFile);

        // Process the CLASSPATH
        String propcp = compilerConfig.getClasspath();
        if (propcp != null && propcp.length() != 0) {
            StringTokenizer st = new StringTokenizer(propcp, File.pathSeparator);
            List<String> configClasspath = config.getClasspath();
            ArrayList<String> toAdd = new ArrayList<String>();
            while (st.hasMoreTokens()) {
                String entry = st.nextToken();
                if (!configClasspath.contains(entry)) {
                    toAdd.add(entry);
                }
            }
            if (0 < toAdd.size()) {
                ArrayList<String> both = new ArrayList<String>(configClasspath.size() + toAdd.size());
                both.addAll(configClasspath);
                both.addAll(toAdd);
                config.setClasspath(both);
            }
        }

        // Process the OUTJAR
        if (config.getOutputJar() == null) {
            String outJar = compilerConfig.getOutJar();
            if (outJar != null && outJar.length() != 0) {
                config.setOutputJar(new File(outJar));
            }
        }

        // Process the OUTPUT LOCATION MANAGER
        IOutputLocationManager outputLocationManager = compilerConfig.getOutputLocationManager();
        if (config.getCompilationResultDestinationManager() == null && outputLocationManager != null) {
            config.setCompilationResultDestinationManager(new OutputLocationAdapter(outputLocationManager));
        }

        // Process the INPATH
        mergeInto(config.getInpath(), compilerConfig.getInpath());
        // bug 168840 - calling 'setInPath(..)' creates BinarySourceFiles which
        // are used to see if there have been changes in classes on the inpath
        if (config.getInpath() != null) {
            config.setInPath(config.getInpath());
        }

        // Process the SOURCE PATH RESOURCES
        config.setSourcePathResources(compilerConfig.getSourcePathResources());

        // Process the ASPECTPATH
        mergeInto(config.getAspectpath(), compilerConfig.getAspectPath());

        // Process the JAVA OPTIONS MAP
        Map jom = compilerConfig.getJavaOptionsMap();
        if (jom != null) {
            String version = (String) jom.get(CompilerOptions.OPTION_Compliance);
            if (version != null
                    && (version.equals(CompilerOptions.VERSION_1_5) || version.equals(CompilerOptions.VERSION_1_6) || version
                            .equals(CompilerOptions.VERSION_1_7))) {
                config.setBehaveInJava5Way(true);
            }
            config.getOptions().set(jom);
        }

        // Process the NON-STANDARD COMPILER OPTIONS
        configureNonStandardOptions(config);

        compilerConfig.configurationRead();

        ISourceLocation location = null;
        if (config.getConfigFile() != null) {
            location = new SourceLocation(config.getConfigFile(), 0);
        }

        String message = parser.getOtherMessages(true);
        if (null != message) {
            IMessage m = new Message(message, IMessage.ERROR, null, location);
            handler.handleMessage(m);
        }

        // always force model generation in AJDE
        config.setGenerateModelMode(true);
        // always be in incremental mode in AJDE
        config.setIncrementalMode(true);
        // always force proceedOnError in AJDE
        config.setProceedOnError(true);

        config.setProjectEncoding(compilerConfig.getProjectEncoding());
        return config;
    }

    private <T> void mergeInto(Collection<T> target, Collection<T> source) {
        if ((null == target) || (null == source)) {
            return;
        }
        for (T next : source) {
            if (!target.contains(next)) {
                target.add(next);
            }
        }
    }

    /**
     * Helper method for configure build options. This reads all command-line options specified in the non-standard options text
     * entry and sets any corresponding unset values in config.
     */
    private void configureNonStandardOptions(AjBuildConfig config) {

        String nonStdOptions = compiler.getCompilerConfiguration().getNonStandardOptions();
        if (LangUtil.isEmpty(nonStdOptions)) {
            return;
        }

        // Break a string into a string array of non-standard options.
        // Allows for one option to include a ' '. i.e. assuming it has been quoted, it
        // won't accidentally get treated as a pair of options (can be needed for xlint props file option)
        List<String> tokens = new ArrayList<String>();
        int ind = nonStdOptions.indexOf('\"');
        int ind2 = nonStdOptions.indexOf('\"', ind + 1);
        if ((ind > -1) && (ind2 > -1)) { // dont tokenize within double quotes
            String pre = nonStdOptions.substring(0, ind);
            String quoted = nonStdOptions.substring(ind + 1, ind2);
            String post = nonStdOptions.substring(ind2 + 1, nonStdOptions.length());
            tokens.addAll(tokenizeString(pre));
            tokens.add(quoted);
            tokens.addAll(tokenizeString(post));
        } else {
            tokens.addAll(tokenizeString(nonStdOptions));
        }
        String[] args = (String[]) tokens.toArray(new String[] {});

        // set the non-standard options in an alternate build config
        // (we don't want to lose the settings we already have)
        CountingMessageHandler counter = CountingMessageHandler.makeCountingMessageHandler(msgHandlerAdapter);
        AjBuildConfig altConfig = AjdtCommand.genBuildConfig(args, counter);
        if (counter.hasErrors()) {
            return;
        }
        // copy globals where local is not set
        config.installGlobals(altConfig);
    }

    /** Local helper method for splitting option strings */
    private List<String> tokenizeString(String str) {
        List<String> tokens = new ArrayList<String>();
        StringTokenizer tok = new StringTokenizer(str);
        while (tok.hasMoreTokens()) {
            tokens.add(tok.nextToken());
        }
        return tokens;
    }

    /**
     * Helper method to ask the messagehandler to handle the given message
     */
    private void handleMessage(Message msg) {
        compiler.getMessageHandler().handleMessage(msg);
    }

    public void setCustomMungerFactory(Object o) {
        ajBuildManager.setCustomMungerFactory(o);
    }

    public Object getCustomMungerFactory() {
        return ajBuildManager.getCustomMungerFactory();
    }

    public void cleanupEnvironment() {
        ajBuildManager.cleanupEnvironment();
    }

    public AsmManager getStructureModel() {
        return ajBuildManager.getStructureModel();
    }
}

/* *******************************************************************
 * Copyright (c) 1999-2001 Xerox Corporation, 
 *               2002 Palo Alto Research Center, Incorporated (PARC).
 * All rights reserved. 
 * This program and the accompanying materials are made available 
 * under the terms of the Eclipse Public License v1.0 
 * which accompanies this distribution and is available at 
 * http://www.eclipse.org/legal/epl-v10.html 
 *  
 * Contributors: 
 *     Xerox/PARC     initial implementation 
 * ******************************************************************/

package org.aspectj.bridge;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Implement messages. This implementation is immutable if ISourceLocation is immutable.
 */
public class Message implements IMessage {
    private final String message;
    private final IMessage.Kind kind;
    private final Throwable thrown;
    private final ISourceLocation sourceLocation;
    private final String details;
    private final List<ISourceLocation> extraSourceLocations;
    private final boolean declared; // Is it a DEOW ?
    private final int id;
    private final int sourceStart, sourceEnd;

    /**
     * Create a (compiler) error or warning message
     * 
     * @param message the String used as the underlying message
     * @param location the ISourceLocation, if any, associated with this message
     * @param isError if true, use IMessage.ERROR; else use IMessage.WARNING
     */
    public Message(String message, ISourceLocation location, boolean isError) {
        this(message, (isError ? IMessage.ERROR : IMessage.WARNING), null, location);
    }

    public Message(String message, ISourceLocation location, boolean isError, ISourceLocation[] extraSourceLocations) {
        this(message, "", (isError ? IMessage.ERROR : IMessage.WARNING), location, null,
                (extraSourceLocations.length > 0 ? extraSourceLocations : null));
    }

    /**
     * Create a message, handling null values for message and kind if thrown is not null.
     * 
     * @param message the String used as the underlying message
     * @param kind the IMessage.Kind of message - not null
     * @param thrown the Throwable, if any, associated with this message
     * @param sourceLocation the ISourceLocation, if any, associated with this message
     * @param details descriptive information about the message
     * @throws IllegalArgumentException if message is null and thrown is null or has a null message, or if kind is null and thrown
     *         is null.
     */
    public Message(String message, String details, IMessage.Kind kind, ISourceLocation sourceLocation, Throwable thrown,
            ISourceLocation[] extraSourceLocations) {
        this(message, details, kind, sourceLocation, thrown, extraSourceLocations, false, 0, -1, -1);
    }

    public Message(String message, String details, IMessage.Kind kind, ISourceLocation sLoc, Throwable thrown,
            ISourceLocation[] otherLocs, boolean declared, int id, int sourcestart, int sourceend) {
        this.details = details;
        this.id = id;
        this.sourceStart = sourcestart;
        this.sourceEnd = sourceend;
        this.message = ((message != null) ? message : ((thrown == null) ? null : thrown.getMessage()));
        this.kind = kind;
        this.sourceLocation = sLoc;
        this.thrown = thrown;
        if (otherLocs != null) {
            this.extraSourceLocations = Collections.unmodifiableList(Arrays.asList(otherLocs));
        } else {
            this.extraSourceLocations = Collections.emptyList();
        }
        if (null == this.kind) {
            throw new IllegalArgumentException("null kind");
        }
        if (null == this.message) {
            throw new IllegalArgumentException("null message");
        }
        this.declared = declared;
    }

    /**
     * Create a message, handling null values for message and kind if thrown is not null.
     * 
     * @param message the String used as the underlying message
     * @param kind the IMessage.Kind of message - not null
     * @param thrown the Throwable, if any, associated with this message
     * @param sourceLocation the ISourceLocation, if any, associated with this message
     * @throws IllegalArgumentException if message is null and thrown is null or has a null message, or if kind is null and thrown
     *         is null.
     */
    public Message(String message, IMessage.Kind kind, Throwable thrown, ISourceLocation sourceLocation) {
        this(message, "", kind, sourceLocation, thrown, null);
    }
    
}