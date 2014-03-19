# Private .bashrc file for user burger
# PATH modification

export PATH="$PATH:~/bin"

if [[ -d ~/Private/bin ]]
then
export PATH="$PATH:~/Private/bin"
fi

# aliases

alias grep='grep --color=auto'
alias ls='ls --color=auto'
alias ll='ls -l'
alias la='ls -la'
alias l='ll'
alias egrep='grep -E'
alias fgrep='grep -F'
alias svim='sudo vim'
alias spacman='sudo pacman'
alias countdown='sudo shutdown -Ph'
alias R='R -q --vanilla'
alias octave='octave -q'
alias su='su -m'
alias xvkbd='xvkbd -secure'
alias gstat='git status'
alias gp='git pull'


# Environment
export GIT_AUTHOR_NAME="Markus Döring"
export GIT_COMMITTER_NAME="Markus Döring"
export GIT_AUTHOR_EMAIL="webmaster@burgerdev.de"
export GIT_PAGER=less
export GIT_EDITOR=vim 

export EDITOR=vim
export PAGER=less


##### function defs
# password generation 
# left hand only
randpw(){
</dev/urandom tr -dc '0-9a-zA-Z!§#+&' | head -c16; echo ""
}

# all
randpw_safe(){
</dev/urandom tr -dc '1234567890!@$%&=?ß+zuioplkjhmnMNJKLUIOP.-_:qwertQWERTasdfgASDFGyxcvbYXCVB' | head -c25; echo ""
}



# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

###############################
#           DOWNLOAD          #
# If non-zero, print the last command's return value
PROMPT_COMMAND="export prompt_ans=\$?"

function _prompt_print_return()
{
    if [[ ! -z $1 && $1 != 0 ]]
    then
        echo -n "[$1]"
    fi
}

# If non-zero, print the number of currently running jobs
function _prompt_print_jobs()
{
    local j=$(jobs | wc -l | awk '{ print $1 }')

    if [ "$j" -ne 0 ]
    then
        echo -n "{$j}"
    fi
}

# Set the prompt color depending on the user's root-ness
function _prompt_color()
{
    if [ $EUID -eq 0 ]
    then
        color=31
    else
        color=32
    fi

    echo -e -n "\033[1;${color}m"
}

# Note that I've split $PS1 onto several lines.
# If you combine onto one line, remove the backslashes at the end of lines
#export PS1="\[\$(_prompt_color)\]\u@\h\[\033[1;34m\]:\w \[\033[1;36m\]\$(_prompt_print_jobs)\[\033[1;31m\]\$(_prompt_print_return \$prompt_ans)\[\033[1;34m\]\$\[\033[00m\] "
export PS1="\[\$(_prompt_color)\]\u@\h\[\033[1;34m\]:\w \[\033[1;36m\]\$(_prompt_print_jobs)\[\033[1;31m\]\$(_prompt_print_return \$prompt_ans)\[\033[1;34m\]\n\$\[\033[00m\] "

export PS2="\[\033[1;34m\]>\[\033[00m\] "
export PS3="\[\033[1;34m\]#?\[\033[00m\] "
export PS4="\[\033[1;34m\][\${LINENO}]+\[\033[00m\] "


#        END DOWNLOAD        #
##############################



# Commented out, don't overwrite xterm -T "title" -n "icontitle" by default.
# If this is an xterm set the title to user@host:dir
#case "$TERM" in
#xterm*|rxvt*)
#    PROMPT_COMMAND='echo -ne "\033]0;${USER}@${HOSTNAME}: ${PWD}\007"'
#    ;;
#*)
#    ;;
#esac

# enable bash completion in interactive shells
if [ -f /etc/bash_completion ] && ! shopt -oq posix; then
    . /etc/bash_completion
fi

# if the command-not-found package is installed, use it
if [ -x /usr/lib/command-not-found -o -x /usr/share/command-not-found ]; then
	function command_not_found_handle {
	        # check because c-n-f could've been removed in the meantime
                if [ -x /usr/lib/command-not-found ]; then
		   /usr/bin/python /usr/lib/command-not-found -- $1
                   return $?
                elif [ -x /usr/share/command-not-found ]; then
		   /usr/bin/python /usr/share/command-not-found -- $1
                   return $?
		else
		   return 127
		fi
	}
fi
