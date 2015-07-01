/*
 * CS354: Operating Systems. 
 * Purdue University
 * Example that shows how to read one line with simple editing
 * using raw terminal.
 */

#include <cstdlib>
#include <cstdio>
#include <cstring>

#include <unistd.h>
#include <termios.h>

#define MAX_BUFFER_LINE 2048

// Buffer where line is stored
int line_length, cursor;
char line_buffer[MAX_BUFFER_LINE];
char ent_command[MAX_BUFFER_LINE];

int history_index = 0, history_length = 0;
char** history = NULL;

void read_line_print_usage()
{
  const char * usage = "\n"
    " ctrl-?       Print usage\n"
    " Backspace    Deletes last character\n"
    " Delete       Deletes current character\n"
    " Home         Puts cursor at beginning of line\n"
    " End          Puts cursor at end of line\n"
    " up arrow     See last command in the history\n"
    " down arrow   See next command in the history\n"
    " left arrow   Move cursor left\n"
    " right arrow  Move cursor right\n";

  write(1, usage, strlen(usage));
}

void tty_raw_mode(void)
{
	struct termios tty_attr;
	tcgetattr(0,&tty_attr);

	/* Set raw mode. */
	tty_attr.c_lflag &= (~(ICANON|ECHO));
	tty_attr.c_cc[VTIME] = 0;
	tty_attr.c_cc[VMIN] = 1;
     
	tcsetattr(0,TCSANOW,&tty_attr);
}

char * read_line() {

  // Set terminal in raw mode
  tty_raw_mode();

  history_index = history_length;
  line_length = 0;
  cursor = 0;
  line_buffer[0] = 0;

  // Read one line until enter is typed
  while (1) {

    // Read one character in raw mode.
    char ch;
    read(0, &ch, 1);

    if (ch>=32 && ch!=127) {
      // It is a printable character. 
      int i = 0;
      for( i = line_length; i >= cursor; --i ) {
        line_buffer[ i+1 ] = line_buffer[ i ];
      }
      line_buffer[ cursor ] = ch;
      ++line_length;
      ++cursor;

      // If max number of character reached return.
      if (line_length==MAX_BUFFER_LINE-2) break;

      // Do echo
      write(1,&line_buffer[cursor-1], line_length - cursor+1);
      for( i = 0; i < (line_length-cursor); ++i ) {
        ch = 8;
        write(1,&ch,1);
      }
    }
    else if (ch==10) {
      // <Enter> was typed. Return line
      
      // Print newline
      write(1,&ch,1);

      break;
    }
    else if (ch == 31) {
      // ctrl-?
      read_line_print_usage();
      line_buffer[0]=0;
      break;
    }
    else if (ch == 8 || ch == 127) {
      // <backspace> was typed. Remove previous character read.
      if( !cursor ) continue;

      // Go back one character
      ch = 8;
      write(1,&ch,1);

      int i = 0;
      for( i=cursor-1; i < line_length-1; ++i ) {
        line_buffer[i] = line_buffer[i+1];
      }
      --cursor;
      --line_length;

      line_buffer[line_length] = 0;
      write(1,&line_buffer[cursor],line_length-cursor);

      ch = ' ';
      write(1,&ch,1);

      for( i = 0; i < line_length-cursor+1; ++i ) {
        ch = 8;
        write(1,&ch,1);
      }

    }
    else if (ch==27) {
      // Escape sequence. Read two chars more
      //
      // HINT: Use the program "keyboard-example" to
      // see the ascii code for the different chars typed.
      //
      char ch1; 
      char ch2;
      read(0, &ch1, 1);
      read(0, &ch2, 1);
      if (ch1==91 && ch2==51) {
        char ch3;
        read(0, &ch3, 1);
        if( ch3 == 126 ) {
          //delete key
          if( cursor == line_length )	continue;

          int i = 0;
          for( i=cursor; i < line_length-1; ++i ) {
            line_buffer[i] = line_buffer[i+1];
          }
          --line_length;

          line_buffer[line_length] = 0;
          write(1,&line_buffer[cursor],line_length-cursor);

          ch = ' ';
          write(1,&ch,1);

          for( i = 0; i < line_length-cursor+1; ++i ) {
            ch = 8;
            write(1,&ch,1);
          }
 
        }
      }
      if (ch1==91 && ch2==49) {
        char ch3;
        read(0, &ch3, 1);
        if( ch3 == 126 ) {
          //home key
          cursor = 0;
        }

      }
      if (ch1==91 && ch2==52) {
        char ch3;
        read(0, &ch3, 1);
        if( ch3 == 126 ) {
          //end key
          cursor = line_length;
        }

      }
      if (ch1==91 && (ch2==65 || ch2==66)) {
	// Up/Down arrow. Print next line in history.

	// Erase old line
	// Print backspaces
	int i = 0;
	for (i =0; i < cursor; i++) {
	  ch = 8;
	  write(1,&ch,1);
	}

	// Print spaces on top
	for (i =0; i < line_length; i++) {
	  ch = ' ';
	  write(1,&ch,1);
	}

	// Print backspaces
	for (i =0; i < line_length; i++) {
	  ch = 8;
	  write(1,&ch,1);
	}

       if( history_index == history_length ) {
	  strcpy( ent_command, line_buffer );
	}

       if( ch2 == 65 )	--history_index;
       else			++history_index;

       if( history_index < 0 )	history_index = 0;
       if( history_index > history_length )	history_index = history_length;

       if( history_index == history_length ) {
         strcpy( line_buffer, ent_command );
       } else {
         strcpy( line_buffer, history[history_index] );
       }
       line_length = cursor = strlen( line_buffer );	

	// echo line
	write(1, line_buffer, line_length);
      }

      if(ch1==91 && ch2==68) {
       //left arrow
       if( cursor != 0 ) {
         cursor--;
         ch = 8;
         write(1,&ch,1);
       }
      }

      if(ch1==91 && ch2==67) {
       //right arrow
       if( cursor != line_length ) {
         cursor++;
         ch = line_buffer[cursor-1];
         write(1,&ch,1);
       }
      }
      
    }

  }

  history = (char**)realloc( history, sizeof(char*)*(history_length+1) );
  history[ history_length ] = (char*)malloc( strlen(line_buffer) );
  strcpy( history[ history_length ], line_buffer );
  ++history_length;
  
  // Add eol and null char at the end of string
  line_buffer[line_length]=10;
  line_length++;
  line_buffer[line_length]=0;

  return line_buffer;
}

