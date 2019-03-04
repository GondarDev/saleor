import AppBar from "@material-ui/core/AppBar";
import ClickAwayListener from "@material-ui/core/ClickAwayListener";
import Grow from "@material-ui/core/Grow";
import Hidden from "@material-ui/core/Hidden";
import IconButton from "@material-ui/core/IconButton";
import LinearProgress from "@material-ui/core/LinearProgress";
import MenuItem from "@material-ui/core/MenuItem";
import Menu from "@material-ui/core/MenuList";
import Paper from "@material-ui/core/Paper";
import Popper from "@material-ui/core/Popper";
import {
  createStyles,
  Theme,
  withStyles,
  WithStyles
} from "@material-ui/core/styles";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import MenuIcon from "@material-ui/icons/Menu";
import Person from "@material-ui/icons/Person";
import SettingsIcon from "@material-ui/icons/Settings";
import * as classNames from "classnames";
import * as React from "react";
import SVG from "react-inlinesvg";

import { appMountPoint } from "../../";
import * as saleorLogo from "../../../images/logo-document.svg";
import { UserContext } from "../../auth";
import {
  drawerWidth,
  navigationBarHeight
} from "../../components/AppLayout/consts";
import MenuList from "../../components/AppLayout/MenuList";
import menuStructure from "../../components/AppLayout/menuStructure";
import ResponsiveDrawer from "../../components/AppLayout/ResponsiveDrawer";
import AppProgress from "../../components/AppProgress";
import MenuToggle from "../../components/MenuToggle";
import Navigator from "../../components/Navigator";
import Anchor from "../../components/TextFieldWithChoice/Anchor";
import Toggle from "../../components/Toggle";
import { configurationMenu, configurationMenuUrl } from "../../configuration";
import i18n from "../../i18n";
import ArrowDropdown from "../../icons/ArrowDropdown";
import { removeDoubleSlashes } from "../../misc";

const styles = (theme: Theme) =>
  createStyles({
    appLoader: {
      height: 2
    },
    arrow: {
      marginLeft: theme.spacing.unit * 2,
      position: "relative",
      top: 6,
      transition: theme.transitions.duration.standard + "ms"
    },
    content: {
      backgroundColor: theme.palette.background.default,
      flexGrow: 1,
      marginLeft: 0,
      marginTop: navigationBarHeight,
      padding: theme.spacing.unit,
      [theme.breakpoints.up("sm")]: {
        padding: theme.spacing.unit * 2
      }
    },
    drawer: {
      background: theme.palette.common.white,
      height: "100vh"
    },
    logo: {
      "& svg": {
        height: "100%"
      },
      display: "block",
      height: 32
    },
    root: {
      display: "grid",
      gridTemplateColumns: `${drawerWidth}px 1fr`
    },
    rotate: {
      transform: "rotate(180deg)"
    },
    sideBar: {
      background: theme.palette.common.white,
      padding: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 4}px`
    }
  });

interface AppLayoutProps {
  children: React.ReactNode;
}
// const AppLayout = withStyles(styles, {
//   name: "AppLayout"
// })(({ classes, children }: AppLayoutProps & WithStyles<typeof styles>) => (
//   <AppProgress>
//     {({ value: isProgressVisible }) => (
//       <UserContext.Consumer>
//         {({ logout, user }) => (
//           <Navigator>
//             {navigate => (
//               <Toggle>
//                 {(
//                   isDrawerOpened,
//                   { toggle: toggleDrawer, disable: closeDrawer }
//                 ) => {
//                   const handleMenuItemClick = (
//                     url: string,
//                     event: React.MouseEvent<any>
//                   ) => {
//                     event.preventDefault();
//                     closeDrawer();
//                     navigate(url);
//                   };
//                   return (
//                     <div className={classes.appFrame}>
//                       <AppBar className={classes.appBar}>
//                         <Toolbar disableGutters className={classes.toolBarMenu}>
//                           <IconButton
//                             color="inherit"
//                             aria-label="open drawer"
//                             onClick={toggleDrawer}
//                             className={classes.menuButton}
//                           >
//                             <MenuIcon />
//                           </IconButton>
//                           <SVG className={classes.logo} src={saleorLogo} />
//                         </Toolbar>
//                         <Toolbar
//                           disableGutters
//                           className={classes.toolBarContent}
//                         >
//                           <div className={classes.spacer} />
//                           <MenuToggle ariaOwns="user-menu">
//                             {({
//                               open: menuOpen,
//                               actions: { open: openMenu, close: closeMenu }
//                             }) => {
//                               const handleLogout = () => {
//                                 close();
//                                 logout();
//                               };
//                               return (
//                                 <Anchor>
//                                   {anchor => (
//                                     <>
//                                       <div
//                                         className={classes.email}
//                                         ref={anchor}
//                                         onClick={
//                                           !menuOpen ? openMenu : undefined
//                                         }
//                                       >
//                                         <Hidden smDown>
//                                           <Typography
//                                             className={classes.emailLabel}
//                                             component="span"
//                                             variant="subheading"
//                                           >
//                                             {user.email}
//                                           </Typography>
//                                           <ArrowDropdown
//                                             className={classNames({
//                                               [classes.arrow]: true,
//                                               [classes.rotate]: menuOpen
//                                             })}
//                                           />
//                                         </Hidden>
//                                         <Hidden mdUp>
//                                           <IconButton
//                                             className={classes.userIcon}
//                                           >
//                                             <Person />
//                                           </IconButton>
//                                         </Hidden>
//                                       </div>
//                                       <Popper
//                                         open={menuOpen}
//                                         anchorEl={anchor.current}
//                                         transition
//                                         disablePortal
//                                         placement="bottom-end"
//                                       >
//                                         {({ TransitionProps, placement }) => (
//                                           <Grow
//                                             {...TransitionProps}
//                                             style={{
//                                               minWidth: "10rem",
//                                               transformOrigin:
//                                                 placement === "bottom"
//                                                   ? "right top"
//                                                   : "right bottom"
//                                             }}
//                                           >
//                                             <Paper>
//                                               <ClickAwayListener
//                                                 onClickAway={closeMenu}
//                                                 mouseEvent="onClick"
//                                               >
//                                                 <Menu>
//                                                   <MenuItem
//                                                     className={
//                                                       classes.userMenuItem
//                                                     }
//                                                     onClick={handleLogout}
//                                                   >
//                                                     {i18n.t("Log out", {
//                                                       context: "button"
//                                                     })}
//                                                   </MenuItem>
//                                                 </Menu>
//                                               </ClickAwayListener>
//                                             </Paper>
//                                           </Grow>
//                                         )}
//                                       </Popper>
//                                     </>
//                                   )}
//                                 </Anchor>
//                               );
//                             }}
//                           </MenuToggle>
//                         </Toolbar>
//                         {isProgressVisible && (
//                           <LinearProgress
//                             className={classes.appLoader}
//                             color="secondary"
//                           />
//                         )}
//                       </AppBar>
//                       <ResponsiveDrawer
//                         onClose={closeDrawer}
//                         open={isDrawerOpened}
//                       >
//                         <div className={classes.menuList}>
//                           <MenuList
//                             menuItems={menuStructure}
//                             user={user}
//                             onMenuItemClick={handleMenuItemClick}
//                           />
//                           <div className={classes.spacer} />
//                           {configurationMenu.filter(menuItem =>
//                             user.permissions
//                               .map(perm => perm.code)
//                               .includes(menuItem.permission)
//                           ).length > 0 && (
//                             <a
//                               className={classes.menuListItem}
//                               href={removeDoubleSlashes(
//                                 appMountPoint + configurationMenuUrl
//                               )}
//                               onClick={event =>
//                                 handleMenuItemClick(configurationMenuUrl, event)
//                               }
//                             >
//                               <SettingsIcon />
//                               <Typography
//                                 aria-label="configure"
//                                 className={classes.menuListItemText}
//                               >
//                                 {i18n.t("Configure")}
//                               </Typography>
//                             </a>
//                           )}
//                         </div>
//                       </ResponsiveDrawer>
//                       <main className={classes.content}>{children}</main>
//                     </div>
//                   );
//                 }}
//               </Toggle>
//             )}
//           </Navigator>
//         )}
//       </UserContext.Consumer>
//     )}
//   </AppProgress>
// ));

const AppLayout = withStyles(styles, {
  name: "AppLayout"
})(({ classes, children }: AppLayoutProps & WithStyles<typeof styles>) => (
  <AppProgress>
    {({ value: isProgressVisible }) => (
      <UserContext.Consumer>
        {({ logout, user }) => (
          <Navigator>
            {navigate => (
              <Toggle>
                {(
                  isDrawerOpened,
                  { toggle: toggleDrawer, disable: closeDrawer }
                ) => {
                  const handleMenuItemClick = (
                    url: string,
                    event: React.MouseEvent<any>
                  ) => {
                    event.preventDefault();
                    closeDrawer();
                    navigate(url);
                  };
                  return (
                    <>
                      {isProgressVisible && (
                        <LinearProgress
                          className={classes.appLoader}
                          color="secondary"
                        />
                      )}
                      <div className={classes.root}>
                        <div className={classes.sideBar}>
                          <SVG className={classes.logo} src={saleorLogo} />
                          <ResponsiveDrawer
                            onClose={closeDrawer}
                            open={isDrawerOpened}
                          >
                            <div className={classes.menuList}>
                              <MenuList
                                menuItems={menuStructure}
                                user={user}
                                onMenuItemClick={handleMenuItemClick}
                              />
                              <div className={classes.spacer} />
                              {configurationMenu.filter(menuItem =>
                                user.permissions
                                  .map(perm => perm.code)
                                  .includes(menuItem.permission)
                              ).length > 0 && (
                                <a
                                  className={classes.menuListItem}
                                  href={removeDoubleSlashes(
                                    appMountPoint + configurationMenuUrl
                                  )}
                                  onClick={event =>
                                    handleMenuItemClick(
                                      configurationMenuUrl,
                                      event
                                    )
                                  }
                                >
                                  <SettingsIcon />
                                  <Typography
                                    aria-label="configure"
                                    className={classes.menuListItemText}
                                  >
                                    {i18n.t("Configure")}
                                  </Typography>
                                </a>
                              )}
                            </div>
                          </ResponsiveDrawer>
                        </div>
                        <div>
                          <div>
                            <MenuToggle ariaOwns="user-menu">
                              {({
                                open: menuOpen,
                                actions: { open: openMenu, close: closeMenu }
                              }) => {
                                const handleLogout = () => {
                                  close();
                                  logout();
                                };
                                return (
                                  <Anchor>
                                    {anchor => (
                                      <>
                                        <div
                                          ref={anchor}
                                          onClick={
                                            !menuOpen ? openMenu : undefined
                                          }
                                        >
                                          <Hidden smDown>
                                            <Typography
                                              component="span"
                                              variant="subheading"
                                            >
                                              {user.email}
                                            </Typography>
                                            <ArrowDropdown
                                              className={classNames({
                                                [classes.arrow]: true,
                                                [classes.rotate]: menuOpen
                                              })}
                                            />
                                          </Hidden>
                                          <Hidden mdUp>
                                            <IconButton
                                              className={classes.userIcon}
                                            >
                                              <Person />
                                            </IconButton>
                                          </Hidden>
                                        </div>
                                        <Popper
                                          open={menuOpen}
                                          anchorEl={anchor.current}
                                          transition
                                          disablePortal
                                          placement="bottom-end"
                                        >
                                          {({ TransitionProps, placement }) => (
                                            <Grow
                                              {...TransitionProps}
                                              style={{
                                                minWidth: "10rem",
                                                transformOrigin:
                                                  placement === "bottom"
                                                    ? "right top"
                                                    : "right bottom"
                                              }}
                                            >
                                              <Paper>
                                                <ClickAwayListener
                                                  onClickAway={closeMenu}
                                                  mouseEvent="onClick"
                                                >
                                                  <Menu>
                                                    <MenuItem
                                                      className={
                                                        classes.userMenuItem
                                                      }
                                                      onClick={handleLogout}
                                                    >
                                                      {i18n.t("Log out", {
                                                        context: "button"
                                                      })}
                                                    </MenuItem>
                                                  </Menu>
                                                </ClickAwayListener>
                                              </Paper>
                                            </Grow>
                                          )}
                                        </Popper>
                                      </>
                                    )}
                                  </Anchor>
                                );
                              }}
                            </MenuToggle>
                          </div>
                          <main className={classes.content}>{children}</main>
                        </div>
                      </div>
                    </>
                  );
                }}
              </Toggle>
            )}
          </Navigator>
        )}
      </UserContext.Consumer>
    )}
  </AppProgress>
));

export default AppLayout;
